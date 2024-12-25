import sys
import asyncio
import uvicorn
from src.main import app
from src.config import HOST, PORT
from src.payment.utils import payment_checkout
from src.server.utils import servers_expired_check


async def main():
    if len(sys.argv) == 3:
        if sys.argv[1] == "--checkout":
            await payment_checkout(sys.argv[2])
            exit(0)
    elif len(sys.argv) == 2:
        if sys.argv[1] == "--expire":
            await servers_expired_check()
            exit(0)

    uvicorn.run("run:app", host=HOST, port=PORT, reload=True)


if __name__ == "__main__":
    asyncio.run(main())
