import aiosqlite
import redis
from src.config import BASE_PATH, DB_PATH, REDIS_HOST, REDIS_PORT

r = redis.asyncio.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}", decode_responses=True)


async def connect():
    connection = await aiosqlite.connect(f"{BASE_PATH}/{DB_PATH}")
    connection.row_factory = aiosqlite.Row
    return connection


async def execute(query: str, parameters: tuple = ()):
    connection = await connect()

    async with connection.execute(query, parameters):
        await connection.commit()


async def fetchone(query: str, parameters: tuple = ()):
    connection = await connect()

    async with connection.execute(query, parameters) as cursor:
        return await cursor.fetchone()


async def fetchall(query: str, parameters: tuple = ()):
    connection = await connect()

    async with connection.execute(query, parameters) as cursor:
        return await cursor.fetchall()
