import base64
from decimal import Decimal
from io import BytesIO
import requests
from requests.auth import HTTPDigestAuth
from qrcode import QRCode
from qrcode.constants import ERROR_CORRECT_L
from src.database import r
from src.logger import logger
from src.config import (
    PAYMENT_LIMIT,
    MONERO_RPC_IP, MONERO_RPC_PORT, MONERO_RPC_USER, MONERO_RPC_PASSWORD, MONERO_RECOVERY_COURSE
)


async def monero_request(method: str, params: dict = None) -> dict | None:
    if params is None:
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
    try:
        usd = await r.get("xmr_course")

        if usd is None:
            res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=monero&vs_currencies=usd")

            if res.status_code == 200:
                usd = res.json()["monero"]["usd"]

                await r.set("xmr_course", usd, ex=28800)

        return usd
    except Exception as e:
        logger.error(e)
        await r.set("xmr_course", MONERO_RECOVERY_COURSE, ex=28800)
        return MONERO_RECOVERY_COURSE


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

    if payments_count is not None:
        ttl = await r.ttl(f"payments_count:{user_id}")

        if int(payments_count) < PAYMENT_LIMIT:
            await r.set(
                f"payments_count:{user_id}",
                int(payments_count) + 1,
                ex=ttl
            )
        else:
            return True
    else:
        await r.set(f"payments_count:{user_id}", 1, ex=86400)


async def draw_qrcode(text: str):
    qr = QRCode(version=1, error_correction=ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(text)
    qr.make()
    img = qr.make_image()
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    qrcode = base64.b64encode(img_bytes.getvalue()).decode("utf-8")

    return qrcode
