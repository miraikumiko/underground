from sqlalchemy import select, update, delete
from datetime import datetime, timedelta
from src.database import async_session_maker
from src.server.models import (
    Server,
    ActiveServer,
    ServerIP
)
from src.server.schemas import (
    ServerCreate,
    ServerRead,
    ServerUpdate,
    ServerDelete,
    ActiveServerCreate,
    ActiveServerRead,
    ActiveServerUpdate,
    ActiveServerDelete,
    ServerIPRead
)
from src.server.rpc import rpc_get_ipv4, rpc_get_ipv6
from src.user.models import User
from src.payment.schemas import PaymentRead


async def crud_add_server(data: ServerCreate) -> None:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                server = Server()
                server.cores = data.cores
                server.ram = data.ram
                server.disk_type = data.disk_type
                server.disk_size = data.disk_size
                server.traffic = data.traffic
                server.location = data.location
                server.avaible = data.avaible
                server.price = data.price

                session.add(server)
            except Exception as e:
                raise e


async def crud_get_servers() -> list[ServerRead]:
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


async def crud_get_server(data: ServerRead) -> ServerRead:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = select(Server).where(Server.id == data.id)
                result = await session.execute(stmt)
                server = result.first()[0]

                return server
            except Exception as e:
                raise e


async def crud_update_server(data: ServerUpdate) -> None:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = update(Server).where(Server.id == data.id).values(
                    cores=data.cores,
                    ram=data.ram,
                    disk_type=data.disk_type,
                    disk_size = data.disk_size,
                    traffic=data.traffic,
                    location=data.location,
                    avaible=data.avaible,
                    price=data.price
                )
                await session.execute(stmt)
            except Exception as e:
                raise e


async def crud_delete_server(data: ServerDelete) -> None:
     async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = delete(Server).where(Server.id == data.id)
                await session.execute(stmt)
            except Exception as e:
                raise e


async def crud_add_active_server(data: ActiveServerCreate) -> None:
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


async def crud_buy_active_server(data: PaymentRead) -> ActiveServer:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = select(Server).where(Server.id == data.server_id)
                result = await session.execute(stmt)
                server = result.first()

                if server is None:
                    raise ValueError("Server doesn't exist")

                ipv4 = await rpc_get_ipv4()
                ipv6 = await rpc_get_ipv6()
                end_at = datetime.now() + timedelta(days=30 * data.month)

                active_server = ActiveServer()
                active_server.user_id = data.user_id
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


async def crud_get_active_servers(user_id: int) -> list[ActiveServerRead]:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = select(ActiveServer).where(ActiveServer.user_id == user_id)
                result = await session.execute(stmt)
                active_servers = result.all()

                return active_servers
            except Exception as e:
                raise e


async def crud_get_active_server(data: ActiveServerRead) -> ActiveServerRead:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = select(ActiveServer).where(ActiveServer.id == data.id)
                result = await session.execute(stmt)
                query = result.first()

                if query is not None:
                    active_server = query[0]
                else:
                    active_server = None

                return active_server
            except Exception as e:
                raise e


async def crud_update_active_server(data: ActiveServerUpdate) -> None:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = update(ActiveServer).where(
                    ActiveServer.id == data.id
                ).values(data)
                await session.execute(stmt)
            except Exception as e:
                raise e


async def crud_delete_active_server(data: ActiveServerDelete) -> None:
     async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = delete(ActiveServer).where(ActiveServer.id == data.id)
                await session.execute(stmt)
            except Exception as e:
                raise e


async def crud_get_server_ips() -> list[ServerIPRead]:
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
