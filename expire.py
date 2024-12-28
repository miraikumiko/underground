import asyncio
from src.payment.utils import expired_check

asyncio.run(expired_check())
