from typing import AsyncGenerator
from redis.asyncio import from_url
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from src.logger import logger
from src.config import (
    DB_TYPE,
    DB_HOST,
    DB_PORT,
    DB_DATABASE,
    DB_USERNAME,
    DB_PASSWORD,
    REDIS_HOST,
    REDIS_PORT,
    REDIS_PASSWORD
)
from src.user.models import User

DATABASE_URL_TEST = "sqlite+aiosqlite:///:memory:"


if DB_TYPE == "sqlite":
    DATABASE_URL = f"{DB_TYPE}+aiosqlite:///{DB_DATABASE}"
elif DB_TYPE == "mariadb":
    DATABASE_URL = f"{DB_TYPE}+aiomysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
elif DB_TYPE == "postgresql":
    DATABASE_URL = f"{DB_TYPE}+asyncpg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
else:
    error_message = "Unsupported database type: {DB_TYPE}"
    logger.critical(error_message)
    raise RuntimeError(error_message)


if REDIS_PASSWORD == '':
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"
else:
    REDIS_URL = f"redis://{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}"


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

r = from_url(REDIS_URL, decode_responses=True)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
