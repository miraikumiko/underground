import asyncpg
from underground.config import DB_URL


async def execute_query(query: str, parameters: tuple = (), fetch: str = None):
	db_pool = await asyncpg.create_pool(dsn=DB_URL, min_size=1, max_size=10)

    async with db_pool.acquire() as connection:
        if fetch == "one":
            return await connection.fetchrow(query, *parameters)

        if fetch == "all":
            return await connection.fetch(query, *parameters)

        return await connection.execute(query, *parameters)


async def execute(query: str, parameters: tuple = ()):
    return await execute_query(query, parameters)


async def fetchone(query: str, parameters: tuple = ()):
    return await execute_query(query, parameters, fetch="one")


async def fetchall(query: str, parameters: tuple = ()):
    return await execute_query(query, parameters, fetch="all")
