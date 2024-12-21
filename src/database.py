import aiosqlite
from redis.asyncio import from_url
from src.config import BASE_PATH, DB_PATH, REDIS_HOST, REDIS_PORT


class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None

    async def connect(self):
        self.connection = await aiosqlite.connect(f"{BASE_PATH}/{DB_PATH}")
        self.connection.row_factory = aiosqlite.Row
        self.cursor = await self.connection.cursor()

    async def close(self):
        await self.cursor.close()
        await self.connection.close()

    async def execute(self, query, parameters=()):
        await self.cursor.execute(query, parameters)
        await self.connection.commit()

    async def fetchone(self, query, parameters=()):
        await self.cursor.execute(query, parameters)
        return await self.cursor.fetchone()

    async def fetchall(self, query, parameters=()):
        await self.cursor.execute(query, parameters)
        return await self.cursor.fetchall()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


r = from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}", decode_responses=True)
