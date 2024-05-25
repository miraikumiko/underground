from datetime import datetime, timedelta
from src.database import r
from src.logger import logger
from src.server.schemas import ServerUpdate
from src.server.crud import crud_read_server, crud_update_server
from src.server.vps import vps_action, vps_upgrade
from src.payment.utils import monero_request, usd_to_xmr


async def payment_request(data: dict, amount: float) -> str:
    res = await monero_request("make_integrated_address")

    address = res["result"]["integrated_address"]
    payment_id = res["result"]["payment_id"]

    amount_xmr = await usd_to_xmr(amount)

    res = await monero_request("make_uri", {
        "address": address,
        "amount": amount_xmr
    })

    payment_uri = res["result"]["uri"]

    data["payment_id"] = payment_id
    data["amount"] = amount_xmr
    data["payment_uri"] = payment_uri

    await r.hset(f"payment:{payment_id}", mapping=data)
    await r.expire(f"payment:{payment_id}", 900)
    await r.set(f'payment_uri:{data["user_id"]}', payment_uri, ex=900)

    return payment_uri


async def payment_checkout(txid: str) -> None:
    res = await monero_request("get_transfer_by_txid", {"txid": txid})

    payment_id = res["result"]["transfer"]["payment_id"]
    amount = res["result"]["transfer"]["amount"]

    payment = await r.hgetall(f"payment:{payment_id}")

    if not payment:
        if payment["amount"] == amount:
            if payment["type"] in ("buy", "pay"):
                server = await crud_read_server(payment["server_id"])
                server_schema = ServerUpdate(
                    end_at=(server.end_at + timedelta(days=(30 * payment["month"]))),
                    active=True
                )

                await crud_update_server(server_schema, server.id)
                await r.delete(f"payment:{payment_id}")
                await r.delete(f'payment_uri:{data["user_id"]}')

                if payment["type"] == "buy":
                    logger.info(f'Server {payment["server_id"]} has been bought by user {payment["user_id"]}')
                else:
                    logger.info(f'Server {payment["server_id"]} has been payed by user {payment["user_id"]}')
            elif payment["type"] == "upgrade":
                server = await crud_read_server(payment["server_id"])
                server_schema = ServerUpdate(
                    end_at=(datetime.now() + timedelta(days=(30 * payment["month"])))
                )

                await crud_update_server(server_schema, server.id)
                await vps_upgrade(server.id, *payment["data"].split(','))

                await r.delete(f"payment:{payment_id}")
                await r.delete(f'payment_uri:{data["user_id"]}')

                logger.info(f'Server {payment["server_id"]} has been upgraded by user {payment["user_id"]}')
