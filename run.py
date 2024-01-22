import uvicorn
import asyncio
from src.main import app
from src.arguments import args
from src.database import db_commit
from src.user.crud import crud_add_user
from src.config import MODE, SOCKET, HOST, PORT


@db_commit
async def main():
    if not (args.email is None or args.password is None):
        await crud_add_user(args.email, args.password)
        print(f'User "{email}" has been created')
        exit(0)

    if MODE == "prod":
        uvicorn.run("run:app", uds=SOCKET, reload=True)
    else:
        uvicorn.run("run:app", host=HOST, port=PORT, reload=True)


if __name__ == "__main__":
    asyncio.run(main())
