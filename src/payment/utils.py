from decimal import Decimal
import requests
from requests.auth import HTTPDigestAuth
from src.database import r
from src.logger import logger
from src.config import (
    MONERO_RPC_IP,
    MONERO_RPC_PORT,
    MONERO_RPC_USER,
    MONERO_RPC_PASSWORD,
    RECOVERY_XMR_COURSE
)


async def monero_request(method: str, params: dict = None) -> dict:
    if params is None:
        params = {}

    response = requests.post(f"http://{MONERO_RPC_IP}:{MONERO_RPC_PORT}/json_rpc",
        json={
            "jsonrpc": "2.0",
            "id": "0",
            "method": method,
            "params": params
        }, headers={"Content-Type": "application/json"},
        auth=HTTPDigestAuth(MONERO_RPC_USER, MONERO_RPC_PASSWORD)
    )

    return response.json()


async def xmr_course() -> float:
    try:
        usd = await r.get("xmr_course")

        if usd is None:
            response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=monero&vs_currencies=usd")
            usd = response.json()["monero"]["usd"]

            await r.set("xmr_course", usd)

        return usd
    except Exception as e:
        logger.error(e)

        await r.set("xmr_course", RECOVERY_XMR_COURSE)

        return RECOVERY_XMR_COURSE


async def usd_to_xmr(usd: float) -> int:
    course = await xmr_course()
    xmr = str(round(Decimal(usd) / Decimal(course), 12))

    while xmr[0:1] == '0' or xmr[0:1] == '.':
        xmr = xmr[1:]

    return int(xmr)
