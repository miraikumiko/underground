import pathlib
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException, WebSocketException
from underground.exceptions import handle_error, http_exception, websocket_exception
from underground.config import HOST, PORT
from underground.auth.router import auth_router
from underground.payment.router import payment_router
from underground.server.router import server_router
from underground.display.router import display_router

current_file_path = pathlib.Path(__file__).resolve()
static_dir = current_file_path.parent.joinpath("static")

routes = [
    Mount("/static", StaticFiles(directory=static_dir), name="static"),
    Mount("/auth", routes=auth_router),
    Mount("/payment", routes=payment_router),
    Mount("/server", routes=server_router),
    Mount("/", routes=display_router)
]

middleware = [
    Middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["*"],
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


def main():
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
