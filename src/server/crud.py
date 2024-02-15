from sqlalchemy import select, update, delete
from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from src.database import async_session_maker
from src.server.models import Server, ActiveServer, ServerIP
from src.server.schemas import (
    ServerCreate,
    ServerUpdate,
    ActiveServerCreate,
    ActiveServerUpdate,
    ActiveServerBuy,
    ActiveServerPay
)
from src.server.rpc import rpc_get_ipv4, rpc_get_ipv6
from src.user.models import User, Discount
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
                result = await session.execute(stmt)
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
                result = await session.execute(stmt)
                server = result.first()[0]

                return server
            except Exception as e:
                raise e


async def crud_update_server(server_id: int, data: ServerUpdate) -> None | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = update(Server).where(Server.id == server_id).values(
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


async def crud_add_active_server(data: ActiveServerCreate, user: User) -> None | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                active_server = ActiveServer()
                active_server.user_id = data.user_id
                active_server.server_id = data.server_id
                active_server.ipv4 = data.ipv4
                active_server.ipv6 = data.ipv6
                active_server.start_at = data.start_at
                active_server.end_at = data.end_at

                session.add(active_server)
            except Exception as e:
                raise e


async def crud_buy_active_server(data: ActiveServerBuy, user: User) -> ActiveServer | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = select(Server).where(Server.id == data.server_id)
                result = await session.execute(stmt)
                server = result.first()

                if server is None:
                    raise ValueError("server doesn't exist")

                ipv4 = await rpc_get_ipv4()
                ipv6 = await rpc_get_ipv6()
                end_at = datetime.now() + timedelta(days=30 * data.month)

                active_server = ActiveServer()
                active_server.user_id = user.id
                active_server.server_id = data.server_id
                active_server.ipv4 = ipv4
                active_server.ipv6 = ipv6
                active_server.end_at = end_at

                session.add(active_server)

                stmt = select(ActiveServer).where(ActiveServer.ipv4 == ipv4)
                result = await session.execute(stmt)
                active_server = result.first()[0]

                return active_server
            except Exception as e:
                raise e


async def crud_get_active_servers(user_id: int) -> list[Row]:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = select(ActiveServer).where(ActiveServer.user_id == user_id)
                result = await session.execute(stmt)
                active_servers = result.all()

                return active_servers
            except Exception as e:
                raise e


async def crud_get_active_server(active_server_id: int) -> Row:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = select(ActiveServer).where(ActiveServer.id == active_server_id)
                result = await session.execute(stmt)
                query = result.first()

                if query is not None:
                    active_server = query[0]
                else:
                    active_server = None

                return active_server
            except Exception as e:
                raise e


async def crud_update_active_server(active_server_id: int, data: ActiveServerUpdate) -> None | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = update(ActiveServer).where(
                    ActiveServer.id == active_server_id
                ).values(data)
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


async def crud_get_server_ips(id: int) -> list[Row] | Exception:
     async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = select(ServerIP)
                result = await session.execute(stmt)
                queries = result.all()
                servers_ips = [query[0] for query in queries]

                return servers_ips
            except Exception as e:
                raise e
