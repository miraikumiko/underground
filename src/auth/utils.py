from starlette.requests import Request
from starlette.websockets import WebSocket
from starlette.exceptions import HTTPException
from websockets.exceptions import ConnectionClosed
from src.database import r, fetchone


async def get_user(request):
    if "auth" in request.cookies:
        user_id = await r.get(f"auth:{request.cookies['auth']}")

        if user_id:
            user = await fetchone("SELECT * from user where id = ?", (user_id,))

            return user


async def active_user(request: Request):
    res = await get_user(request)

    if res:
        return res
    else:
        raise HTTPException(401, "Unauthorized")


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
