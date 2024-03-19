from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from contextlib import asynccontextmanager
from src.database import r
from src.server.router import router as server_router
from src.payment.router import router as payment_router
from src.user.router import router as user_router
from src.auth.router import (
    router as auth_router,
    reset_password_router,
    verify_router
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    FastAPICache.init(RedisBackend(r), prefix="fastapi-cache")
    yield


app = FastAPI(lifespan=lifespan, docs_url="/api/docs", openapi_url="/api/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(server_router)
app.include_router(payment_router)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(reset_password_router, prefix="/api/auth", tags=["auth"])
app.include_router(verify_router, prefix="/api/auth", tags=["auth"])
