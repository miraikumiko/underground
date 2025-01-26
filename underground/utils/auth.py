from starlette.authentication import AuthenticationBackend, AuthCredentials
from starlette.requests import Request
from starlette.websockets import WebSocket, WebSocketDisconnect
from starlette.exceptions import HTTPException
from passlib.context import CryptContext
from underground.database import fetchone

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


class CookieAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn: Request | WebSocket):
        token = conn.cookies.get("auth")

        if token:
            user = await fetchone("SELECT * FROM users WHERE token = ?", (token,))

            if user:
                return AuthCredentials(["authenticated"]), user
