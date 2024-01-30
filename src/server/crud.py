from sqlalchemy import select, update, delete
from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import async_session_maker
from src.server.models import Server
from src.user.models import Discount
from src.server.schemas import (
    ServerCreate,
    ServerUpdate,
    ActiveServerCreate,
    ActiveServerUpdate
)
from src.auth.password import get_password_hash


async def crud_add_server(data: ServerCreate) -> None | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                server = Server()
                server.cores = data.cores
                server.ram = data.ram
                server.disk = data.disk
                server.traffic = data.traffic
                server.location = data.location
                server.avaible = data.avaible
                server.price = data.price

                session.add(server)
            except Exception as e:
                raise e


async def crud_get_servers() -> list[Row] | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = select(Server)
                result = await s.execute(stmt)
                queries = result.all()
                servers = [query[0] for query in queries]

                return servers
            except Exception as e:
                raise e


async def crud_get_server(id: int) -> Row | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = select(Server).where(Server.id == id)
                result = await s.execute(stmt)
                server = result.first()[0]

                return server
            except Exception as e:
                raise e


async def crud_update_server(id: int, data: ServerUpdate) -> None | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
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
            except Exception as e:
                raise e


async def crud_delete_server(id: int) -> None | Exception:
     async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = delete(Server).where(Server.id == id)
                await session.execute(stmt)
            except Exception as e:
                raise e


async def crud_add_active_server(data: ActiveServerCreate) -> None | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = select(User).where(User.id == data.user_id)
                result = await session.execute(stmt)

                user = result.first()

                if user is None:
                    raise Exception("user doesn't exist")

                stmt = select(Server).where(Server.id == data.server_id)
                result = await session.execute(stmt)
                server = result.first()

                if server is None:
                    raise Exception("server doesn't exist")

                active_server = ActiveServer()
                active_server.user_id = data.user_id
                active_server.server_id = data.server_id
                active_server.iso = data.iso
                active_server.ipv4 = data.ipv4
                active_server.ipv6 = data.ipv6
                active_server.start_at = data.start_at
                active_server.end_at = data.end_at
            except Exception as e:
                raise e


async def crud_get_active_servers(user_id: int) -> list[Row]:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = select(column("id")).select_from(ActiveServer).where(ActiveServer.user_id == user_id)
                result = await session.execute(stmt)
                active_servers_id = [row[0] for row in result.all()]
 
                stmt = select(Server).where(Server.id.in_(active_servers_id))
                result = await session.execute(stmt)
                queries = result.all()

                active_servers = []

                for query in queries:
                    data = query[0]
                    server = {
                        "id": data.id,
                        "user_id": data.user_id,
                        "server_id": data.server_id,
                        "iso": data.iso,
                        "ipv4": data.ipv4,
                        "ipv6": data.ipv6,
                        "start_at": data.start_at,
                        "end_at": data.end_at
                    }
                    servers.append(server)

                return active_servers
            except Exception as e:
                raise e


async def crud_get_active_server(user_id: int, server_id: int) -> Row:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = select(ActiveServer).where(ActiveServer.user_id == user_id).filter(ActiveServer.server_id == server_id)
                result = await session.execute(stmt)
                query = result.first()

                if query is not None:
                    active_server = query[0]
                else:
                    active_server = None

                return active_server
            except Exception as e:
                raise e


async def crud_update_active_server(data: ActiveServerUpdate) -> None | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = update(ActiveServer).where(ActiveServer.id == data.server_id).values(
                    user_id=data.user_id,
                    server_id=data.server_id,
                    iso=data.iso,
                    ipv4=data.ipv4,
                    ipv6=data.ipv6,
                    start_at=data.start_at,
                    end_at=data.end_at
                )
                await session.execute(stmt)
            except Exception as e:
                raise e


async def crud_delete_active_server(id: int) -> None | Exception:
     async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = delete(ActiveServer).where(ActiveServer.id == id)
                await session.execute(stmt)
            except Exception as e:
                raise e
