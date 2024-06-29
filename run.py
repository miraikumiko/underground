import sys
import asyncio
import uvicorn
from src.main import app
from src.database import engine
from src.models import Base
from src.arguments import args
from src.logger import logger
from src.config import HOST, PORT
from src.auth.utils import password_helper
from src.user.schemas import UserCreate
from src.user.crud import crud_create_user
from src.payment.payments import payment_checkout
from src.server.utils import servers_expired_check
from src.node.models import *
from src.server.models import *
from src.user.models import *


async def main():
    if not (args.username is None and args.password is None):
        user = UserCreate(
            username=args.username,
            password=password_helper.hash(args.password),
            is_active=args.is_active
        )

        await crud_create_user(user)

        print(f"User {args.username} has been created")
        sys.exit(0)
    elif args.checkout:
        logger.info("Start processing checkout with txid %s", args.checkout)
        await payment_checkout(args.checkout)
        sys.exit(0)
    elif args.expire:
        await servers_expired_check()
        sys.exit(0)
    elif args.migrate:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        sys.exit(0)

    uvicorn.run("run:app", host=HOST, port=PORT, reload=True)


if __name__ == "__main__":
    asyncio.run(main())
