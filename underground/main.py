import sys
import asyncio
import contextlib
import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException, WebSocketException
from underground.exceptions import handle_error, http_exception, websocket_exception
from underground.config import BASE_DIR, HOST, PORT
from underground.database import database
from underground.utils.auth import CookieAuthBackend
from underground.utils.payment import set_xmr_course, payment_checkout, expiration_check
from underground.routers.auth import auth_router
from underground.routers.payment import payment_router
from underground.routers.server import server_router
from underground.routers.display import display_router

routes = [
    Mount("/static", StaticFiles(directory=BASE_DIR.joinpath("static")), name="static"),
    Mount("/auth", routes=auth_router),
    Mount("/payment", routes=payment_router),
    Mount("/server", routes=server_router),
    Mount("/", routes=display_router)
]

middleware = [
    Middleware(
        AuthenticationMiddleware,
        backend=CookieAuthBackend()
    ),
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

scheduler = BackgroundScheduler()


@contextlib.asynccontextmanager
async def lifespan(app: Starlette):
    # Startup
    loop = asyncio.get_running_loop()

    scheduler.add_job(
        lambda: asyncio.run_coroutine_threadsafe(expiration_check(), loop),
        IntervalTrigger(days=1),
        id="expiration_check"
    )
    scheduler.add_job(
        lambda: asyncio.run_coroutine_threadsafe(set_xmr_course(app), loop),
        IntervalTrigger(hours=12),
        id="set_xmr_course"
    )

    scheduler.start()

    await database.connect()
    await expiration_check()
    await set_xmr_course(app)

    yield

    # Shutdown
    await database.disconnect()

    scheduler.shutdown()


app = Starlette(
    routes=routes,
    middleware=middleware,
    exception_handlers=exception_handlers,
    lifespan=lifespan
)


def main():
    if len(sys.argv) > 1:
        txid = sys.argv[1]
        course = app.state.XMR_COURSE
        asyncio.run(payment_checkout(txid, course))
    else:
        uvicorn.run(app, host=HOST, port=PORT)
