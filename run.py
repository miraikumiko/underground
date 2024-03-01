import uvicorn
import asyncio
from src.main import app
from src.arguments import args
from src.logger import logger
from src.config import HOST, PORT
from src.user.crud import (
    crud_create_user,
    crud_create_user_settings
)
from src.payment.payments import payment_checkout


async def main():
    if not (args.email is None and args.password is None):
        user_id = await crud_create_user(
            args.password,
            args.email,
            args.is_active,
            args.is_superuser,
            args.is_verified
        )
        await crud_create_user_settings({"user_id": user_id})

        print(f'User "{args.email}" has been created')
        exit(0)
    elif args.checkout is not None:
        await payment_checkout(args.checkout)
        logger.info(f"Start processing checkout with txid {args.checkout}")
        exit(0)

    uvicorn.run("run:app", host=HOST, port=PORT, reload=True)


if __name__ == "__main__":
    asyncio.run(main())
