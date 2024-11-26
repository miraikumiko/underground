from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from fastapi import Request, WebSocket, HTTPException
from src.database import r
from src.user.crud import crud_read_user

password_helper = PasswordHash((Argon2Hasher(),))


async def get_active_user(request):
    if "auth" in request.cookies:
        user_id = await r.get(f"auth:{request.cookies["auth"]}")

        if user_id is not None:
            user = await crud_read_user(int(user_id))

            if user:
                if user.is_active:
                    return user
                else:
                    return 2
            else:
                return 1


async def active_user(request: Request):
    res = await get_active_user(request)

    if res == 1:
        raise HTTPException(403, "d|Forbidden")
    elif res == 2:
        raise HTTPException(401, "d|Unauthorized")
    else:
        return res


async def active_user_opt(request: Request):
    res = await get_active_user(request)

    if res == 1 or res == 2:
        return None
    else:
        return res


async def active_user_ws(request: WebSocket):
    if "auth" in request.cookies:
        res = await get_active_user(request)

        if res == 1:
            raise HTTPException(403, "d|Forbidden")
        elif res == 2:
            raise HTTPException(401, "d|Unauthorized")
        else:
            return res
