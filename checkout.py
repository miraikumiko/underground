import sys
import asyncio
from decimal import Decimal
from src.database import execute, fetchone
from src.payment.utils import monero_request


async def payment_checkout(txid: str):
    res = await monero_request("get_transfer_by_txid", {"txid": txid})
    payment_id = res["result"]["transfer"]["payment_id"]
    amount = res["result"]["transfer"]["amount"]

    payment = await fetchone("SELECT * FROM payment WHERE payment_id = ?", (payment_id,))

    if payment:
        user = await fetchone("SELECT * FROM user WHERE id = ?", (payment["user_id"],))

        user_balance = Decimal(user["balance"])
        xmr_amount = Decimal(amount) / Decimal(1_000_000_000_000)
        balance = float(round(user_balance + xmr_amount * Decimal(course), 2))

        await execute("UPDATE user SET balance = ? WHERE id = ?", (balance, user["id"]))
        await execute("DELETE FROM payment WHERE id = ?", (payment["id"],))


asyncio.run(payment_checkout(sys.argv[1]))
