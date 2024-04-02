from datetime import datetime, timedelta
from src.database import r
from src.logger import logger
from src.server.schemas import ServerUpdate
from src.server.crud import crud_read_server, crud_update_server
from src.payment.utils import monero_request, usd_to_xmr


async def payment_request(data: dict, amount: float) -> str:
    response = await monero_request("make_integrated_address")

    address = response["result"]["integrated_address"]
    payment_id = response["result"]["payment_id"]

    amount_xmr = await usd_to_xmr(amount)

    response = await monero_request("make_uri", {
        "address": address,
        "amount": amount_xmr
    })

    payment_uri = response["result"]["uri"]

    data["payment_id"] = payment_id
    data["amount"] = amount_xmr
    data["payment_uri"] = payment_uri

    await r.hset(f"payment:{payment_id}", mapping=data)
    await r.expire(f"payment:{payment_id}", 3600)
    await r.set(f'payment_uri:{data["user_id"]}', payment_uri, 1800)

    return payment_uri


async def payment_checkout(txid: str) -> None:
    response = await monero_request("get_transfer_by_txid", {"txid": txid})

    payment_id = response["result"]["transfer"]["payment_id"]
    amount = response["result"]["transfer"]["amount"]

    payment = await r.hgetall(f"payment:{payment_id}")

    if payment is not None:
        if payment["amount"] == amount:
            server = await crud_read_server(payment["server_id"])
            server_schema = ServerUpdate(
                end_at=server.end_at + timedelta(days=30 * payment["month"]),
                active=True
            )

            await crud_update_server(server_schema, server.id)
            await r.delete(f"payment:{payment_id}")
            await r.delete(f'payment_uri:{data["user_id"]}')

            logger.info(f'Server has been bought/payed by user with id {payment["user_id"]}')
