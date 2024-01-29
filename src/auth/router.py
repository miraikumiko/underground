from fastapi import FastAPI

from fastapi import Depends
from src.auth.utils import users, auth_backend
from src.user.schemas import UserCreate, UserUpdate, UserRead


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


def add_reset_password_router(app: FastAPI):
    app.include_router(
        users.get_reset_password_router(),
        prefix="/api/auth",
        tags=["auth"]
    )


def add_verify_router(app: FastAPI):
    app.include_router(
        users.get_verify_router(UserRead),
        prefix="/auth",
        tags=["auth"]
    )


def add_users_router(app: FastAPI):
    app.include_router(
        users.get_users_router(UserRead, UserUpdate),
        prefix="/api/users",
        tags=["users"]
    )
