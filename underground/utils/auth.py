from argon2 import PasswordHasher
from starlette.authentication import AuthenticationBackend, AuthCredentials
from starlette.requests import Request
from starlette.websockets import WebSocket
from underground.database import database
from underground.models import User

ph = PasswordHasher()


class CookieAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn: Request | WebSocket):
        token = conn.cookies.get("auth")

        if token:
            user = await database.fetch_one(User.select().where(User.c.token == token))

            if user:
                return AuthCredentials(["authenticated"]), user
