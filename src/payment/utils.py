from decimal import Decimal
from datetime import timedelta
import requests
from requests.auth import HTTPDigestAuth
from src.database import r, execute, fetchone
from src.config import (
    PAYMENT_TIME, PAYMENT_LIMIT,
    VDS_DAYS,
    MONERO_RPC_IP, MONERO_RPC_PORT, MONERO_RPC_USER, MONERO_RPC_PASSWORD
)
from src.server.vds import vds_migrate, vds_upgrade
from src.display.utils import draw_qrcode


async def monero_request(method: str, params: dict = None) -> dict | None:
    if not params:
        params = {}

    res = requests.post(
        f"http://{MONERO_RPC_IP}:{MONERO_RPC_PORT}/json_rpc",
        json={"jsonrpc": "2.0", "id": "0", "method": method, "params": params},
        headers={"Content-Type": "application/json"},
        auth=HTTPDigestAuth(MONERO_RPC_USER, MONERO_RPC_PASSWORD)
    )

    if res.status_code == 200:
        return res.json()


async def xmr_course() -> float:
    usd = await r.get("xmr_course")

    if not usd:
        res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=monero&vs_currencies=usd")

        if res.status_code == 200:
            usd = res.json()["monero"]["usd"]

            await r.set("xmr_old_course", usd, ex=24 * 60 * 60 * 7)
            await r.set("xmr_course", usd, ex=12 * 60 * 60)
        else:
            usd = await r.get("xmr_old_course")
            await r.set("xmr_course", usd, ex=12 * 60 * 60)

    return usd


async def usd_to_xmr(usd: float) -> int:
    course = await xmr_course()
    xmr = str(round(Decimal(usd) / Decimal(course), 12)).replace('.', '')

    while xmr[0:1] == '0':
        xmr = xmr[1:]

    return int(xmr)


async def check_active_payment(user_id: int) -> dict | None:
    payment_uri = await r.get(f"payment_uri:{user_id}")

    if payment_uri:
        ttl = await r.ttl(f"payment_uri:{user_id}")
        qrcode = await draw_qrcode(payment_uri)

        return {"qrcode": qrcode, "payment_uri": payment_uri, "ttl": ttl}


async def check_payment_limit(user_id: int) -> bool | None:
    payments_count = await r.get(f"payments_count:{user_id}")

    if payments_count:
        ttl = await r.ttl(f"payments_count:{user_id}")

        if int(payments_count) < PAYMENT_LIMIT:
            await r.set(f"payments_count:{user_id}", int(payments_count) + 1, ex=ttl)
        else:
            return True
    else:
        await r.set(f"payments_count:{user_id}", 1, ex=86400)


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
