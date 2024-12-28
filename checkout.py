import sys
import asyncio
from src.payment.utils import payment_checkout

asyncio.run(payment_checkout(sys.argv[1]))
