from datetime import timedelta
from src.config import PAYMENT_TIME, VDS_DAYS
from src.database import r, execute, fetchone
from src.logger import logger
from src.server.vds import vds_migrate, vds_upgrade
from src.payment.utils import monero_request, usd_to_xmr


async def payment_request(ptype: str, server_id: int, vds_id: int = None) -> dict:
    res = await monero_request("make_integrated_address")
    address = res["result"]["integrated_address"]
    payment_id = res["result"]["payment_id"]

    server = await fetchone("SELECT * FROM server WHERE id = ?", (server_id,))

    if ptype == "upgrade" and vds_id:
        vds = await fetchone("SELECT * FROM vds WHERE id = ?", (vds_id,))
    else:
        vds = await fetchone("SELECT * FROM vds WHERE id = ?", (server["vds_id"],))

    amount = await usd_to_xmr(vds["price"])

    res = await monero_request("make_uri", {"address": address, "amount": amount})
    payment_uri = res["result"]["uri"]
    payment_data = {"type": ptype, "payment_id": payment_id, "amount": amount}

    if server_id:
        payment_data["server_id"] = server_id

    if vds_id:
        payment_data["vds_id"] = vds_id

    await r.hset(f"payment:{payment_id}", mapping=payment_data)
    await r.expire(f"payment:{payment_id}", 60 * PAYMENT_TIME)
    await r.set(f"payment_uri:{server['user_id']}", payment_uri, ex=60 * PAYMENT_TIME)

    return {"payment_uri": payment_uri, "ttl": 60 * PAYMENT_TIME}


async def payment_checkout(txid: str) -> None:
    res = await monero_request("get_transfer_by_txid", {"txid": txid})
    payment_id = res["result"]["transfer"]["payment_id"]
    amount = res["result"]["transfer"]["amount"]

    payment = await r.hgetall(f"payment:{payment_id}")

    if payment:
        if int(payment["amount"]) == amount:
            server = await fetchone("SELECT * FROM server WHERE id = ?", (int(payment["server_id"]),))

            if payment["type"] == "buy":
                await execute("UPDATE server SET is_active = ? WHERE id = ?", (1, server["id"]))
            elif payment["type"] == "pay":
                await execute(
                    "UPDATE server SET end_at = ?, is_active = ? WHERE id = ?",
                    (server.end_at + timedelta(days=VDS_DAYS), 1, server["id"])
                )
            elif payment["type"] == "upgrade":
                node = await fetchone("SELECT * FROM node WHERE id = ?", (server["node_id"],))
                vds = await fetchone("SELECT * FROM vds WHERE id = ?", (server["vds_id"],))

                await vds_upgrade(server["id"], node["ip"], vds)

                dst_node_id = await r.get(f"node_to_migrate:{server['id']}")
                upgrade_vds_id = await r.get(f"unupgraded_server:{server['id']}")

                # Migrate if needed
                if dst_node_id:
                    dst_node = await fetchone("SELECT * FROM node WHERE id = ?", (int(dst_node_id),))
                    await execute(
                        "UPDATE server SET in_upgrade = ?, vds_id = ?, node_id = ?",
                        (0, int(upgrade_vds_id), dst_node["id"])
                    )
                    await vds_migrate(server["id"], node["ip"], dst_node)
                else:
                    await execute("UPDATE server SET in_upgrade = ?, vds_id = ?", (0, int(upgrade_vds_id)))

                # Delete markers
                await r.delete(f"node_to_migrate:{server['id']}")
                await r.delete(f"unupgraded_server:{server['id']}")

            await r.delete(f"payment:{payment_id}")
            await r.delete(f"payment_uri:{server['user_id']}")

            logger.info(f"Checkout {payment_id} {server['id']}")
