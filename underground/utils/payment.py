from decimal import Decimal
from datetime import date, timedelta
import httpx
from starlette.applications import Starlette
from underground.config import (
    VDS_DAYS, VDS_EXPIRED_DAYS,
    MONERO_RPC_IP, MONERO_RPC_PORT, MONERO_RPC_USERNAME, MONERO_RPC_PASSWORD
)
from underground.database import database
from underground.models import User, Payment, Node, Server
from underground.utils.server import vds_delete


async def monero_request(method: str, params: dict = None) -> dict | None:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://{MONERO_RPC_IP}:{MONERO_RPC_PORT}/json_rpc",
            json={"jsonrpc": "2.0", "id": "0", "method": method, "params": params},
            headers={"Content-Type": "application/json"},
            auth=httpx.DigestAuth(MONERO_RPC_USERNAME, MONERO_RPC_PASSWORD)
        )

    return response.json()


async def get_xmr_course() -> float:
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.coingecko.com/api/v3/simple/price?ids=monero&vs_currencies=usd")
        course = response.json()["monero"]["usd"]

        return course


async def set_xmr_course(app: Starlette) -> None:
    course = await get_xmr_course()
    app.state.XMR_COURSE = course


async def usd_to_xmr(usd: float, course: float) -> int:
    xmr = str(round(Decimal(usd) / Decimal(course), 12)).replace('.', '')

    while xmr[0:1] == '0':
        xmr = xmr[1:]

    return int(xmr)


async def request_vds(user_id: int, vds: dict, node: dict) -> None:
    servers = await database.fetch_all(Server.select())

    # Reservation port for VNC
    vnc_port = 5900

    if servers:
        up = [server.vnc_port for server in servers if server.node_id == node.id]

        while vnc_port in up:
            vnc_port += 1

    # Registration of new server
    start_at = date.today()
    end_at = (start_at + timedelta(days=VDS_DAYS)).strftime("%Y-%m-%d %H:%M:%S")

    await database.execute(
        Node.update().where(Node.c.id == node.id).values(
            cores_available=node.cores_available - vds.cores,
            ram_available=node.ram_available - vds.ram,
            disk_size_available=node.disk_size_available - vds.disk_size
        )
    )
    await database.execute(
        Server.insert().values(
            vnc_port=vnc_port,
            start_at=start_at,
            end_at=end_at,
            vds_id=vds.id,
            node_id=node.id,
            user_id=user_id
        )
    )


async def payment_request(user_id: int, amount: float) -> str:
    res = await monero_request("make_integrated_address")
    address = res["result"]["integrated_address"]
    payment_id = res["result"]["payment_id"]

    res = await monero_request("make_uri", {"address": address, "amount": amount})
    payment_uri = res["result"]["uri"]

    await database.execute(Payment.insert().values(payment_id=payment_id, user_id=user_id))

    return payment_uri


async def payment_checkout(txid: str, course: float) -> None:
    res = await monero_request("get_transfer_by_txid", {"txid": txid})
    payment_id = res["result"]["transfer"]["payment_id"]
    amount = res["result"]["transfer"]["amount"]

    payment = await database.fetch_one(Payment.select().where(Payment.c.id == payment_id))

    if payment:
        user = await database.fetch_one(User.select().where(User.c.id == payment.user_id))
        user_balance = Decimal(user.balance)
        xmr_amount = Decimal(amount) / Decimal(1_000_000_000_000)
        balance = float(round(user_balance + xmr_amount * Decimal(course), 2))

        await database.execute(User.update().where(User.c.id == user.id).values(balance=balance))
        await database.execute(Payment.delete().where(Payment.c.id == payment.id))


async def expiration_check() -> None:
    servers = await database.fetch_all(Server.select())

    for server in servers:
        if server.end_at + timedelta(days=VDS_EXPIRED_DAYS) <= date.today():
            node = await database.fetch_one(Node.select().where(Node.c.id == server.node_id))
            await database.execute(Server.delete().where(server.c.id == server.id))
            await vds_delete(server.id, node.ip)
