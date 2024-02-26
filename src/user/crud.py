from string import ascii_letters, digits
from random import choices
from sqlalchemy import select, update, delete, column
from pydantic import EmailStr
from src.database import async_session_maker, r
from src.user.models import User, UserSettings
from src.server.models import Server
from src.user.schemas import UserRead, UserUpdate
from src.auth.password import get_password_hash
from src.mail import sendmail
from src.config import (
    SERVICE_NAME,
    DOMAIN,
    ONION_DOMAIN,
    I2P_DOMAIN
)


async def crud_add_user(
    password: str,
    email: str = None,
    is_active: bool = True,
    is_superuser: bool = False,
    is_verified: bool = False
) -> None | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = select(User).where(User.email == email)
                result = await session.execute(stmt)
                user = result.first()

                if user is None:
                    user = User()
                    user.email = email
                    user.hashed_password = get_password_hash(password)
                    user.is_active = is_active
                    user.is_superuser = is_superuser
                    user.is_verified = is_verified

                    session.add(user)
                else:
                    raise Exception("user already exist")
            except Exception as e:
                raise e


async def crud_get_users() -> list[UserRead] | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = select(User)
                result = await session.execute(stmt)
                queries = result.all()
                users = []

                for query in queries:
                    data = query[0]
                    user = {
                        "id": data.id,
                        "email": data.email,
                        "is_active": data.is_active,
                        "is_superuser": data.is_superuser,
                        "is_verified": data.is_verified
                    }
                    users.append(user)

                return users
            except Exception as e:
                raise e


async def crud_get_user(id: int) -> UserRead | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = select(User).where(User.id == id)
                result = await session.execute(stmt)
                query = result.first()
                data = query[0]
                user = {
                    "id": data.id,
                    "email": data.email,
                    "is_active": data.is_active,
                    "is_superuser": data.is_superuser,
                    "is_verified": data.is_verified
                }

                return user
            except Exception as e:
                raise e


async def crud_get_user_by_email(email: EmailStr) -> UserRead | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = select(User).where(User.email == email)
                result = await session.execute(stmt)
                query = result.first()
                user = query[0]

                return user
            except Exception as e:
                raise e


async def crud_update_user(id: int, data: UserUpdate) -> None | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                hpw = get_password_hash(data.password)
                stmt = update(User).where(User.id == id).values(
                    email=data.email,
                    hashed_password=hpw,
                    is_active=data.is_active,
                    is_superuser=data.is_superuser,
                    is_verified=data.is_verified
                )
                await session.execute(stmt)
            except Exception as e:
                raise e


async def crud_update_user_email(user_id: int, email: EmailStr) -> None | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = update(User).where(User.id == user_id).values(
                    email=email,
                    is_verified=False
                )

                chars = ascii_letters + digits
                length = 32
                token = ''.join(choices(chars, k=length))

                subject = f"[{SERVICE_NAME}] email verification"
                body = f"""
                Your verification link is:
                https://{DOMAIN}/api/user/verify/{token}
                http://{ONION_DOMAIN}/api/user/verify/{token}
                http://{I2P_DOMAIN}/api/user/verify/{token}
                """

                await session.execute(stmt)
                await r.set(user_id, token, 86400)
                await sendmail(subject, body, email)
            except Exception as e:
                raise e


async def crud_verify_user_email(email: EmailStr, token: str) -> None | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = select(User).where(User.email == email)
                result = await session.execute(stmt)
                user = result.first()

                if user is not None:
                    try:
                        subject = f"[{SERVICE_NAME}] verification"
                        body = f"Your token for verification: {token}"

                        await sendmail(subject, body, email)
                    except Exception as e:
                        raise e
                else:
                    raise Exception("Email not exist or user turned off password reseting")
            except Exception as e:
                raise e


async def crud_update_user_password(user_id: int, old_password: str, new_password: str) -> None | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                old_hpw = get_password_hash(old_password)

                stmt = select(column("hashed_password")).select_from(User).where(User.user_id == user_id)
                hashed_password = await session.execute(stmt)

                if old_hpw != hashed_password:
                    raise Exception("invalid old password")

                new_hpw = get_password_hash(old_password)
                
                stmt = update(User).where(User.id == user_id).values(hashed_password=new_hpw)

                await session.execute(stmt)
            except Exception as e:
                raise e


async def crud_forgot_user_password(email: EmailStr, token: str) -> None | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = select(User).where(User.email == email)
                result = await session.execute(stmt)
                user = result.first()[0]

                stmt = select(UserSettings).where(UserSettings.user_id == user.id)
                result = await session.execute(stmt)
                reset_password = result.first()[0]

                if reset_password:
                    try:
                        subject = f"[{SERVICE_NAME}] password reset"
                        body = f"Your token for password reset: {token}"

                        await sendmail(subject, body, email)
                    except Exception as e:
                        raise e
                else:
                    raise Exception("Email not exist or user turned off password reseting")
            except Exception as e:
                raise e


async def crud_delete_user(id: int) -> None | Exception:
     async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = delete(User).where(User.id == id)
                await session.execute(stmt)
            except Exception as e:
                raise e


async def crud_add_user_settings(user_id: int) -> None | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = select(User).where(User.id == user_id)
                result = await session.execute(stmt)
                user = result.first()

                stmt = select(UserSettings).where(UserSettings.user_id == user_id)
                result = await session.execute(stmt)
                user_settings = result.first()

                if user is None:
                    raise Exception(f"user with id {user_id} doesn't exist")

                if user_settings is None:
                    session.add_all([
                        UserSettings(user_id=user_id)
                    ])
                    await session.commit()
                else:
                    raise Exception("user settings already exist")
            except Exception as e:
                raise e
