from decimal import Decimal
import requests
from requests.auth import HTTPDigestAuth
from src.config import (
    MONERO_RPC_IP,
    MONERO_RPC_PORT,
    MONERO_RPC_USER,
    MONERO_RPC_PASSWORD
)


async def monero_request(method: str, params: dict = {}) -> dict:
    response = requests.post(f"http://{MONERO_RPC_IP}:{MONERO_RPC_PORT}", {
        "jsonrpc": "2.0",
        "id": "0",
        "method": method,
        "params": params
    }, auth=HTTPDigestAuth(MONERO_RPC_USER, MONERO_RPC_PASSWORD))

    return response.json()


async def usd_to_xmr(usd: float) -> int | Exception:
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=monero&vs_currencies=usd")
        xmr_course = response.json()["monero"]["usd"]
        xmr = str(round(Decimal(usd) / Decimal(xmr_course), 12))

        while xmr[0:1] == '0' or xmr[0:1] == '.':
            xmr = xmr[1:]

        return int(xmr)
    except Exception as e:
        raise e
