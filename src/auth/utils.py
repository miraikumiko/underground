from fastapi import Request, HTTPException
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from src.database import r
from src.user.crud import crud_read_user

password_helper = PasswordHash((Argon2Hasher(),))


async def active_user(request: Request):
    has_cookie = "auth" in request.cookies
    auth_token = request.cookies["auth"] if has_cookie else None

    if not has_cookie or auth_token is None:
        raise HTTPException(status_code=401)

    user_id = await r.get(f"auth:{auth_token}")

    if user_id is None:
        raise HTTPException(status_code=401)

    user = await crud_read_user(int(user_id))

    if user is not None and user.is_active:
        return user
    else:
        raise HTTPException(status_code=401)


async def auth_check(request: Request):
    has_cookie = "auth" in request.cookies
    auth_token = request.cookies["auth"] if has_cookie else None

    if not has_cookie or auth_token is None:
        return None

    user_id = await r.get(f"auth:{auth_token}")

    if user_id is None:
        return None

    user = await crud_read_user(int(user_id))

    if user is not None and user.is_active:
        return user
    else:
        return None
