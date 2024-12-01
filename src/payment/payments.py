from datetime import timedelta
from src.database import r
from src.logger import logger
from src.server.schemas import ServerUpdate
from src.server.crud import crud_read_server, crud_update_server
from src.server.vds import vds_upgrade
from src.payment.crud import crud_read_vds
from src.payment.utils import monero_request, usd_to_xmr


async def payment_request(ptype: str, server_id: int, vds_id: int = None) -> dict:
    res = await monero_request("make_integrated_address")
    address = res["result"]["integrated_address"]
    payment_id = res["result"]["payment_id"]

    server = await crud_read_server(server_id)

    if ptype == "upgrade" and vds_id:
        if vds_id is not None:
            vds = await crud_read_vds(vds_id)
        else:
            msg = "Missing vds_id parameter"
            logger.error(msg)
            raise Exception(msg)
    else:
        vds = await crud_read_vds(server.vds_id)

    amount = await usd_to_xmr(vds.price)

    res = await monero_request("make_uri", {"address": address, "amount": amount})
    payment_uri = res["result"]["uri"]
    payment_data = {"type": ptype, "payment_id": payment_id, "amount": amount}

    if server_id is not None:
        payment_data["server_id"] = server_id
    if vds_id is not None:
        payment_data["vds_id"] = vds_id

    await r.hset(f"payment:{payment_id}", mapping=payment_data)
    await r.expire(f"payment:{payment_id}", 900)
    await r.set(f"payment_uri:{server.user_id}", payment_uri, ex=900)

    return {"payment_uri": payment_uri, "ttl": 900}


async def payment_checkout(txid: str) -> None:
    res = await monero_request("get_transfer_by_txid", {"txid": txid})
    payment_id = res["result"]["transfer"]["payment_id"]
    amount = res["result"]["transfer"]["amount"]

    payment = await r.hgetall(f"payment:{payment_id}")

    if not payment:
        if payment["amount"] == amount:
            server = await crud_read_server(payment["server_id"])

            if payment["type"] == "buy":
                server_schema = ServerUpdate(active=True)
                await crud_update_server(server_schema, payment["server_id"])
            elif payment["type"] == "pay":
                server_schema = ServerUpdate(
                    end_at=(server.end_at - server.start_at + timedelta(days=31)),
                    active=True
                )
                await crud_update_server(server_schema, payment["server_id"])
            elif payment["type"] == "upgrade":
                await vds_upgrade(payment["server_id"], payment["vds_id"])

            await r.delete(f"payment:{payment_id}")
            await r.delete(f'payment_uri:{server.user_id}')

            logger.info(f'Checkout {payment_id} {payment["server_id"]}')
