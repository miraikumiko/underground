import aiosqlite
from underground.config import DB_PATH


async def execute_query(query: str, parameters: tuple = (), fetch: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        async with await db.execute(query, parameters) as cursor:
            if fetch == "one":
                return await cursor.fetchone()

            if fetch == "all":
                return await cursor.fetchall()

            await db.commit()
            return cursor.lastrowid


async def execute(query: str, parameters: tuple = ()):
    return await execute_query(query, parameters)


async def fetchone(query: str, parameters: tuple = ()):
    return await execute_query(query, parameters, fetch="one")


async def fetchall(query: str, parameters: tuple = ()):
    return await execute_query(query, parameters, fetch="all")
