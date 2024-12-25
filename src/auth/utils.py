from starlette.requests import Request
from starlette.websockets import WebSocket, WebSocketDisconnect
from starlette.exceptions import HTTPException
from src.database import r, fetchone


async def get_user(request):
    if "auth" in request.cookies:
        cursor = 0

        while True:
            cursor, keys = await r.scan(cursor, match=f"*:auth:{request.cookies['auth']}", count=100)

            if keys:
                user_id = keys[0].split(':')[0]
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
            raise WebSocketDisconnect(code=1008)
