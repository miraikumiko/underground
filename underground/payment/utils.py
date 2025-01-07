from decimal import Decimal
from datetime import datetime, timedelta, UTC
import httpx
from underground.config import VDS_DAYS, MONERO_RPC_IP, MONERO_RPC_PORT, MONERO_RPC_USERNAME, MONERO_RPC_PASSWORD
from underground.database import execute, fetchall


async def monero_request(method: str, params: dict = None) -> dict | None:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://{MONERO_RPC_IP}:{MONERO_RPC_PORT}/json_rpc",
            json={"jsonrpc": "2.0", "id": "0", "method": method, "params": params},
            headers={"Content-Type": "application/json"},
            auth=httpx.DigestAuth(MONERO_RPC_USERNAME, MONERO_RPC_PASSWORD)
        )

    return response.json()


async def xmr_course() -> float:
    with open("/tmp/xmr_course") as file:
        return float(file.read())


async def usd_to_xmr(usd: float) -> int:
    course = await xmr_course()
    xmr = str(round(Decimal(usd) / Decimal(course), 12)).replace('.', '')

    while xmr[0:1] == '0':
        xmr = xmr[1:]

    return int(xmr)


async def request_vds(user_id: int, vds: dict, node: dict) -> None:
    servers = await fetchall("SELECT * FROM server")

    # Reservation port for VNC
    vnc_port = 5900

    if servers:
        up = [server["vnc_port"] for server in servers if server["node_id"] == node["id"]]

        while vnc_port in up:
            vnc_port += 1

    # Registration of new server
    start_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S.%f")
    end_at = datetime.now() + timedelta(days=VDS_DAYS)

    await execute(
        "UPDATE node SET cores_available = ?, ram_available = ?, disk_size_available = ? WHERE id = ?",
        (
            node["cores_available"] - vds["cores"],
            node["ram_available"] - vds["ram"],
            node["disk_size_available"] - vds["disk_size"],
            node["id"]
        )
    )
    await execute(
        "INSERT INTO server (vnc_port, start_at, end_at, vds_id, node_id, user_id) VALUES (?, ?, ?, ?, ?, ?)",
        (vnc_port, start_at, end_at, vds["id"], node["id"], user_id)
    )


async def payment_request(user_id: int, amount: float) -> str:
    res = await monero_request("make_integrated_address")
    address = res["result"]["integrated_address"]
    payment_id = res["result"]["payment_id"]

    res = await monero_request("make_uri", {"address": address, "amount": amount})
    payment_uri = res["result"]["uri"]

    await execute("INSERT INTO payment (payment_id, user_id) VALUES (?, ?)", (payment_id, user_id))

    return payment_uri
