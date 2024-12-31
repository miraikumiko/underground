from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.exceptions import HTTPException, WebSocketException
from starlette.middleware.cors import CORSMiddleware
from src.exceptions import handle_error, http_exception, websocket_exception
from src.config import BASE_PATH
from src.auth.router import auth_router
from src.payment.router import payment_router
from src.server.router import server_router
from src.display.router import display_router

routes = [
    Mount("/static", StaticFiles(directory=f"{BASE_PATH}/static"), name="static"),
    Mount("/auth", routes=auth_router),
    Mount("/payment", routes=payment_router),
    Mount("/server", routes=server_router),
    Mount("/", routes=display_router)
]

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
]

exception_handlers = {
    Exception: handle_error,
    HTTPException: http_exception,
    WebSocketException: websocket_exception
}

app = Starlette(routes=routes, middleware=middleware, exception_handlers=exception_handlers)
