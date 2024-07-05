from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from fastapi import Request, WebSocket
from src.database import r
from src.user.crud import crud_read_user

password_helper = PasswordHash((Argon2Hasher(),))


async def active_user(request: Request):
    if "auth" in request.cookies:
        user_id = await r.get(f'auth:{request.cookies["auth"]}')

        if user_id is not None:
            user = await crud_read_user(int(user_id))

            if user.is_active:
                return user


async def active_user_ws(request: WebSocket):
    if "auth" in request.cookies:
        user_id = await r.get(f'auth:{request.cookies["auth"]}')

        if user_id is not None:
            user = await crud_read_user(int(user_id))

            if user.is_active:
                return user
