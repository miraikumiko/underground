import aiosqlite
import redis
from src.config import BASE_PATH, DB_PATH, REDIS_HOST, REDIS_PORT

r = redis.asyncio.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}", decode_responses=True)


async def execute(query: str, parameters: tuple = ()):
    async with aiosqlite.connect(f"{BASE_PATH}/{DB_PATH}") as db:
        db.row_factory = aiosqlite.Row

        async with await db.execute(query, parameters) as cursor:
            await db.commit()
            return cursor.lastrowid


async def fetchone(query: str, parameters: tuple = ()):
    async with aiosqlite.connect(f"{BASE_PATH}/{DB_PATH}") as db:
        db.row_factory = aiosqlite.Row

        async with await db.execute(query, parameters) as cursor:
            return await cursor.fetchone()


async def fetchall(query: str, parameters: tuple = ()):
    async with aiosqlite.connect(f"{BASE_PATH}/{DB_PATH}") as db:
        db.row_factory = aiosqlite.Row

        async with await db.execute(query, parameters) as cursor:
            return await cursor.fetchall()
