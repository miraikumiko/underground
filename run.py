import uvicorn
import asyncio
from src.main import app
from src.arguments import args
from src.logger import logger
from src.config import HOST, PORT
from src.user.crud import (
    crud_add_user,
    crud_add_user_settings,
    crud_get_user_by_email
)
from src.payment.payments import payment_checkout


async def main():
    if not (args.email is None and args.password is None):
        await crud_add_user(
            args.password,
            args.email,
            args.is_active,
            args.is_superuser,
            args.is_verified
        )
        user = await crud_get_user_by_email(args.email)
        await crud_add_user_settings(user.id)

        print(f'User "{args.email}" has been created')
        exit(0)
    elif args.checkout is not None:
        await payment_checkout(args.checkout)
        logger.info(f"Start payment checkout with txid = {args.checkout}")
        exit(0)

    uvicorn.run("run:app", host=HOST, port=PORT, reload=True)


if __name__ == "__main__":
    asyncio.run(main())
