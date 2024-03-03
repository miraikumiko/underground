from typing import Optional
from fastapi import Request, Depends
from fastapi_users import BaseUserManager, IntegerIDMixin
from src.database import User, get_user_db
from src.mail import sendmail
from src.logger import logger
from src.config import SERVICE_NAME, SECRET
from src.user.crud import (
    crud_create_user_settings,
    crud_read_user_settings
)
from src.user.schemas import UserSettingsCreate


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, _: Optional[Request] = None):
        logger.info(f"User {user.id} has registered.")
        await crud_create_user_settings(UserSettingsCreate(**{"user_id": user.id}))

    async def on_after_forgot_password(self, user: User, token: str, _: Optional[Request] = None):
        user_settings = await crud_read_user_settings(user.id)

        if user_settings.reset_password:
            subject = f"[{SERVICE_NAME}] password reset"
            body = f"Your token for password reset: {token}"

            await sendmail(subject, body, user.email)

            logger.info(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_reset_password(self, user: User, _: Optional[Request] = None):
        logger.info(f"User {user.id} has reset their password.")

    async def on_after_request_verify(self, user: User, token: str, _: Optional[Request] = None):
        subject = f"[{SERVICE_NAME}] verification"
        body = f"Your token for verification: {token}"

        await sendmail(subject, body, user.email)

        logger.info(f"Verification requested for user {user.id}. Verification token: {token}")

    async def on_after_verify(self, user: User, _: Optional[Request] = None):
        logger.info(f"User {user.id} has been verified")

    async def on_after_delete(self, user: User, _: Optional[Request] = None):
        logger.info(f"User {user.id} is successfully deleted")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
