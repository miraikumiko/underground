import asyncio
from sys import argv
from src.payment.utils import payment_checkout

asyncio.run(payment_checkout(argv[1]))
