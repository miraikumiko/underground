from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    CookieTransport,
    RedisStrategy,
    AuthenticationBackend
)
from passlib.context import CryptContext
from src.auth.manager import get_user_manager
from src.database import r
from src.user.models import User
from src.config import TOKEN_LIFETIME

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(r, lifetime_seconds=TOKEN_LIFETIME)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

cookie_transport = CookieTransport(cookie_max_age=TOKEN_LIFETIME)

auth_backend = AuthenticationBackend(
    name="cookie+redis",
    transport=cookie_transport,
    get_strategy=get_redis_strategy
)

users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend]
)
