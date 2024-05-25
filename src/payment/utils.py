import requests
from requests.auth import HTTPDigestAuth
from datetime import datetime
from decimal import Decimal
from fastapi.responses import JSONResponse
from src.database import r
from src.server.crud import crud_read_server
from src.logger import logger
from src.config import (
    MONERO_RPC_IP, MONERO_RPC_PORT, MONERO_RPC_USER, MONERO_RPC_PASSWORD,
    RECOVERY_XMR_COURSE,
    PRICE_CPU, PRICE_RAM, PRICE_DISK, PRICE_IPV4
)


async def monero_request(method: str, params: dict = None) -> dict | None:
    if params is None:
        params = {}

    res = requests.post(f"http://{MONERO_RPC_IP}:{MONERO_RPC_PORT}/json_rpc",
        json={
            "jsonrpc": "2.0",
            "id": "0",
            "method": method,
            "params": params
        }, headers={"Content-Type": "application/json"},
        auth=HTTPDigestAuth(MONERO_RPC_USER, MONERO_RPC_PASSWORD)
    )
    
    if res.status_code == 200:
        return res.json()


async def xmr_course() -> float:
    try:
        usd = await r.get("xmr_course")

        if usd is None:
            res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=monero&vs_currencies=usd")

            if res.status_code == 200:
                usd = res.json()["monero"]["usd"]

                await r.set("xmr_course", usd, ex=86400)

                return usd
        else:
            return usd
    except Exception as e:
        logger.error(e)
        await r.set("xmr_course", RECOVERY_XMR_COURSE, ex=86400)
        return RECOVERY_XMR_COURSE


async def usd_to_xmr(usd: float) -> int:
    course = await xmr_course()
    xmr = str(round(Decimal(usd) / Decimal(course), 12))

    while xmr[0:1] == '0' or xmr[0:1] == '.':
        xmr = xmr[1:]

    return int(xmr)


async def get_prices():
    prices = {
        "cpu": {
            1: PRICE_CPU,
            2: 2 * PRICE_CPU * 2,
            4: 4 * PRICE_CPU * 3,
            8: 8 * PRICE_CPU * 4
        },
        "ram": {
            1024: PRICE_RAM,
            2048: 2 * PRICE_RAM * 2,
            4096: 4 * PRICE_RAM * 3,
            8192: 8 * PRICE_RAM * 4
        },
        "disk": {
            32: PRICE_DISK,
            64: PRICE_DISK * 2,
            128: PRICE_DISK * 4,
            256: PRICE_DISK * 8,
            512: PRICE_DISK * 16,
            1024: PRICE_DISK * 32
        },
        "ipv4": PRICE_IPV4,
        "xmr": await xmr_course()
    }

    return prices


async def check_active_payment(user_id: int) -> JSONResponse:
    payment_uri = await r.get(f"payment_uri:{user_id}")

    if payment_uri is not None:
        ttl = await r.ttl(f"payment_uri:{user_id}")

        return JSONResponse({
            "payment_uri": payment_uri,
            "ttl": ttl,
            "detail": "You already have payment"
        }, status_code=203)


async def check_payment_limit(user_id: int) -> None:
    payments_count = await r.get(f"payments_count:{user_id}")

    if payments_count is not None:
        ttl = await r.ttl(f"payments_count:{user_id}")

        if int(payments_count) < 3:
            await r.set(
                f"payments_count:{user_id}",
                int(payments_count) + 1,
                ex=ttl
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="You can make only 3 payment request per day"
            )
    else:
        await r.set(f"payments_count:{user_id}", 1, ex=86400)


async def make_payment_request(
    ptype: str,
    user_id: int,
    server_id: int,
    cores: int,
    ram: int,
    disk: int,
    month: int = None,
    data: str = None
) -> dict:
    payment_data = {
        "type": ptype,
        "user_id": user_id,
        "server_id": server_id,
        "month": month,
        "data": data
    }

    if ptype == "upgrade":
        server = await crud_read_server(server_id)

        payed_month = (server.end_at - datetime.now()) // 30

        amount = ((
            (cores * prices["cpu"][cores]) +
            (ram * prices["ram"][ram]) +
            (disk * prices["disk"][disk]) +
            (prices["ipv4"])
        ) - (
            (server.cores * prices["cpu"][cores]) +
            (server.ram * prices["ram"][ram]) +
            (server.disk * prices["disk"][disk]) +
            (prices["ipv4"])
        )) * payed_month

        payment_data["month"] = payed_month
    else:
        amount = (
            (cores * prices["cpu"][cores]) +
            (ram * prices["ram"][ram]) +
            (disk * prices["disk"][disk]) +
            (prices["ipv4"])
        ) * month

    payment_uri = await payment_request(payment_data, float(amount))
    ttl = await r.ttl(f"payment_uri:{user_id}")

    return {"payment_uri": payment_uri, "ttl": ttl}
