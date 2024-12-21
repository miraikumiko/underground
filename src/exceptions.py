from starlette.requests import Request
from starlette.websockets import WebSocket
from starlette.middleware.exceptions import HTTPException, WebSocketException
from src.display.utils import t_error


async def handle_error(request: Request, _: Exception):
    return await t_error(request, 500, "Internal Server Error")


async def http_exception(request: Request, exc: HTTPException):
    return await t_error(request, exc.status_code, exc.detail)


async def websocket_exception(websocket: WebSocket, _: WebSocketException):
    await websocket.close(code=1008)
