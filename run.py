import uvicorn
import asyncio
from src.main import app
from src.arguments import args
from src.logger import logger
from src.config import HOST, PORT
from src.user.schemas import UserCreate, UserSettingsCreate
from src.user.crud import (
    crud_create_user,
    crud_create_user_settings
)
from src.payment.payments import payment_checkout
from src.server.utils import active_servers_expired_check


async def main():
    if not (args.username is None and args.password is None):
        user = UserCreate(
            username=args.username,
            email=args.email if args.email else None,
            password=args.password,
            is_active=args.is_active,
            is_superuser=args.is_superuser,
            is_verified=args.is_verified
        )

        user_id = await crud_create_user(user)
        user_settings = UserSettingsCreate(user_id=user_id)
        await crud_create_user_settings(user_settings)

        print(f'User "{args.username}" has been created')
        exit(0)
    elif args.checkout:
        logger.info(f"Start processing checkout with txid {args.checkout}")
        await payment_checkout(args.checkout)
        exit(0)
    elif args.expire:
        await active_servers_expired_check()
        exit(0)

    uvicorn.run("run:app", host=HOST, port=PORT, reload=True)


if __name__ == "__main__":
    asyncio.run(main())
