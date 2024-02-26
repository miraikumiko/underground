from fastapi import FastAPI
from src.auth.utils import users, auth_backend
from src.user.schemas import UserCreate, UserUpdate, UserRead


users_router = users.get_users_router(UserRead, UserUpdate)
auth_router = users.get_auth_router(auth_backend)
register_router = users.get_register_router(UserRead, UserCreate)
reset_password_router = users.get_reset_password_router()
verify_router = users.get_verify_router(UserRead)
