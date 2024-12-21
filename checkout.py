import asyncio
from sys import argv
from src.logger import logger
from src.payment.payments import payment_checkout

logger.info("Start processing checkout with txid %s", argv[1])
asyncio.run(payment_checkout(argv[1]))
