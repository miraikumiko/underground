from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.errors import ServerErrorMiddleware
from src.config import BASE_PATH
from src.display.utils import t_error
from src.auth.router import router as auth_router
from src.payment.router import router as payment_router
from src.server.router import router as server_router
from src.display.router import router as display_router


async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return await t_error(request, exc.status_code, exc.detail)


routes = [
    Route("/static", StaticFiles(directory=f"{BASE_PATH}/static"), name="static"),
    Mount("/api/auth", routes=auth_router),
    Mount("/api/payment", routes=payment_router),
    Mount("/api/server", routes=server_router),
    Mount("/", routes=display_router)
]

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    ),
    Middleware(ServerErrorMiddleware, handler=custom_http_exception_handler)
]

app = Starlette(routes=routes, middleware=middleware)
