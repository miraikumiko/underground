from fastapi import FastAPI
from src.auth.utils import users, auth_backend
from src.user.schemas import UserRead, UserCreate


def add_auth_router(app: FastAPI):
    app.include_router(
        users.get_auth_router(auth_backend),
        prefix="/api/auth",
        tags=["auth"]
    )


def add_register_router(app: FastAPI):
    app.include_router(
        users.get_register_router(UserRead, UserCreate),
        prefix="/api/auth",
        tags=["auth"]
    )
