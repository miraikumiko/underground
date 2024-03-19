from fastapi import Request, HTTPException
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    BearerTransport,
    CookieTransport,
    RedisStrategy,
    AuthenticationBackend
)
from src.database import r
from src.config import AUTH_TRANSPORT, TOKEN_LIFETIME
from src.auth.manager import get_user_manager
from src.user.models import User
from src.user.crud import crud_read_user


def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(r, lifetime_seconds=TOKEN_LIFETIME)


if AUTH_TRANSPORT == "bearer":
    transport = BearerTransport(tokenUrl="auth/jwt/login")
else:
    transport = CookieTransport(cookie_max_age=TOKEN_LIFETIME)

auth_backend = AuthenticationBackend(
    name="Auth",
    transport=transport,
    get_strategy=get_redis_strategy
)

users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend]
)


async def active_user(request: Request):
    if "fastapiusersauth" in request.cookies:
        token = request.cookies["fastapiusersauth"]
    else:
        raise HTTPException(status_code=401)

    user_id = await r.get(f"fastapi_users_token:{token}")

    if user_id is not None:
        user = await crud_read_user(int(user_id))

        if user.is_active:
            return user
        else:
            raise HTTPException(status_code=401)
    else:
        raise HTTPException(status_code=401)


async def admin(request: Request):
    if "fastapiusersauth" in request.cookies:
        token = request.cookies["fastapiusersauth"]
    else:
        raise HTTPException(status_code=401)

    user_id = await r.get(f"fastapi_users_token:{token}")

    if user_id is not None:
        user = await crud_read_user(int(user_id))

        if user.is_active and user.is_superuser and user.is_verified:
            return user
        else:
            raise HTTPException(status_code=401)
    else:
        raise HTTPException(status_code=401)
