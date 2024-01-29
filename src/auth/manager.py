from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin
from typing import Optional
from src.database import User, get_user_db
from src.user.crud import crud_forgot_user_password, crud_verify_user_email
from src.config import SECRET
from src.logger import logger


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET


    async def on_after_register(self, user: User, request: Optional[Request] = None):
        logger.info(f"User {user.id} has registered.")


    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        logger.info(f"User {user.id} has forgot their password. Reset token: {token}")
        await crud_forgot_user_password(user.email, token)


    async def on_after_reset_password(self, user: User, request: Optional[Request] = None):
        logger.info(f"User {user.id} has reset their password.")


    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        logger.info(f"Verification requested for user {user.id}. Verification token: {token}")
        await crud_verify_user_email(user.email, token)


    async def on_after_verify(self, user: User, request: Optional[Request] = None):
        logger.info(f"User {user.id} has been verified")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
