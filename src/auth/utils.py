from fastapi import Request, WebSocket
from websockets.exceptions import ConnectionClosed
from src.database import r
from src.crud import crud_read
from src.auth.models import User
from src.display.exceptions import DisplayException


async def get_user(request):
    if "auth" in request.cookies:
        user_id = await r.get(f"auth:{request.cookies['auth']}")

        if user_id:
            user = await crud_read(User, User.id, int(user_id))

            return user


async def active_user(request: Request):
    res = await get_user(request)

    if res:
        return res
    else:
        raise DisplayException(401, "Unauthorized")


async def active_user_opt(request: Request):
    res = await get_user(request)

    return res


async def active_user_ws(request: WebSocket):
    if "auth" in request.cookies:
        res = await get_user(request)

        if res:
            return res
        else:
            raise ConnectionClosed
