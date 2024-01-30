from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from contextlib import asynccontextmanager
from src.database import r
from src.server.router import add_server_router
from src.auth.router import (
    add_auth_router,
    add_register_router,
    add_reset_password_router,
    add_verify_router,
    add_users_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    FastAPICache.init(RedisBackend(r), prefix="fastapi-cache")
    yield


app = FastAPI(lifespan=lifespan, docs_url="/api/docs", openapi_url="/api/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

add_server_router(app)
add_users_router(app)
add_auth_router(app)
add_register_router(app)
add_reset_password_router(app)
add_verify_router(app)
