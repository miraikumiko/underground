from datetime import timedelta
from src.config import PAYMENT_TIME, VDS_DAYS
from src.database import r
from src.logger import logger
from src.node.crud import crud_read_node
from src.server.schemas import ServerUpdate
from src.server.crud import crud_read_server, crud_update_server
from src.server.vds import vds_migrate, vds_upgrade
from src.payment.crud import crud_read_vds
from src.payment.utils import monero_request, usd_to_xmr


async def payment_request(ptype: str, server_id: int, vds_id: int = None) -> dict:
    res = await monero_request("make_integrated_address")
    address = res["result"]["integrated_address"]
    payment_id = res["result"]["payment_id"]

    server = await crud_read_server(server_id)

    if ptype == "upgrade" and vds_id:
        vds = await crud_read_vds(vds_id)
    else:
        vds = await crud_read_vds(server.vds_id)

    amount = await usd_to_xmr(vds.price)

    res = await monero_request("make_uri", {"address": address, "amount": amount})
    payment_uri = res["result"]["uri"]
    payment_data = {"type": ptype, "payment_id": payment_id, "amount": amount}

    if server_id:
        payment_data["server_id"] = server_id

    if vds_id:
        payment_data["vds_id"] = vds_id

    await r.hset(f"payment:{payment_id}", mapping=payment_data)
    await r.expire(f"payment:{payment_id}", 60 * PAYMENT_TIME)
    await r.set(f"payment_uri:{server.user_id}", payment_uri, ex=(60 * PAYMENT_TIME))

    return {"payment_uri": payment_uri, "ttl": 60 * PAYMENT_TIME}


async def payment_checkout(txid: str) -> None:
    res = await monero_request("get_transfer_by_txid", {"txid": txid})
    payment_id = res["result"]["transfer"]["payment_id"]
    amount = res["result"]["transfer"]["amount"]

    payment = await r.hgetall(f"payment:{payment_id}")

    if payment:
        if int(payment["amount"]) == amount:
            server = await crud_read_server(int(payment["server_id"]))

            if payment["type"] == "buy":
                server_schema = ServerUpdate(is_active=True)
                server_schema = server_schema.rm_none_attrs()
                await crud_update_server(server_schema, server.id)
            elif payment["type"] == "pay":
                server_schema = ServerUpdate(
                    end_at=server.end_at + timedelta(days=VDS_DAYS),
                    is_active=True
                )
                server_schema = server_schema.rm_none_attrs()
                await crud_update_server(server_schema, server.id)
            elif payment["type"] == "upgrade":
                node = await crud_read_node(server.node_id)
                vds = await crud_read_vds(server.vds_id)

                await vds_upgrade(server, node, vds)
                dst_node_id = await r.get(f"node_to_migrate:{server.id}")
                upgrade_vds_id = await r.get(f"unupgraded_server:{server.id}")
                server_schema = ServerUpdate(in_upgrade=False, vds_id=int(upgrade_vds_id))

                if dst_node_id:
                    server_node = await crud_read_node(server.node_id)
                    dst_node = await crud_read_node(int(dst_node_id))
                    server_schema = server_schema.node_id = dst_node.id

                    await vds_migrate(server, server_node, dst_node)

                server_schema = server_schema.rm_none_attrs()
                await crud_update_server(server_schema, server.id)

                await r.delete(f"unupgraded_server:{server.id}")

            await r.delete(f"payment:{payment_id}")
            await r.delete(f"payment_uri:{server.user_id}")

            logger.info(f"Checkout {payment_id} {server.id}")
