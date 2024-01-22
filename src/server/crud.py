from sqlalchemy import select, update, delete
from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import async_session_maker
from src.server.models import Server
from src.server.schemas import ServerCreate, ServerUpdate
from src.auth.utils import get_password_hash


async def crud_add_server(data: ServerCreate) -> None | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            server = Server()
            server.cores = data.cores
            server.ram = data.ram
            server.disk = data.disk
            server.traffic = data.traffic
            server.location = data.location
            server.avaible = data.avaible
            server.price = data.price

            result = session.add(server)


async def crud_get_servers() -> list[Row]:
    async with async_session_maker() as session:
        async with session.begin():
            stmt = select(Server)
            result = await s.execute(stmt)
            queries = result.all()
            servers = [query[0] for query in queries]

            return servers


async def crud_get_server(id: int) -> Row:
    async with async_session_maker() as session:
        async with session.begin():
            stmt = select(Server).where(Server.id == id)
            result = await s.execute(stmt)
            server = result.first()[0]

            return server


async def crud_update_server(id: int, data: ServerUpdate) -> None | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            stmt = update(Server).where(Server.id == id).values(
                cores=data.cores,
                ram=data.ram,
                disk=data.disk,
                traffic=data.traffic,
                location=data.location,
                avaible=data.avaible,
                price=data.price
            )
            await session.execute(stmt)


async def crud_delete_server(id: int) -> None | Exception:
     async with async_session_maker() as session:
        async with session.begin():
            stmt = delete(Server).where(Server.id == id)
            await session.execute(stmt)
