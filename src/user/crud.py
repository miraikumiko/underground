from sqlalchemy import select, update, delete, column
from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import async_session_maker
from src.user.models import User
from src.server.models import Server, ActiveServer
from src.user.schemas import UserCreate, UserRead, UserUpdate
from src.server.schemas import ActiveServerCreate, ActiveServerUpdate
from src.auth.utils import get_password_hash


async def crud_add_user(email: str, password: str) -> None | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = select(User).where(User.email == email)
                result = await session.execute(stmt)
                user = result.first()

                if user is not None:
                    raise Exception("user already exist")
                else:
                    hpw = get_password_hash(password)
                    session.add_all([User(email=email, hashed_password=hpw)])
                    await session.commit()
            except Exception as e:
                raise e


async def crud_get_users() -> list[UserRead] | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = select(User)
                result = await session.execute(stmt)
                queries = result.all()
                users = []

                for query in queries:
                    data = query[0]
                    user = {
                        "id": data.id,
                        "email": data.email,
                        "is_active": data.is_active,
                        "is_superuser": data.is_superuser,
                        "is_verified": data.is_verified
                    }
                    users.append(user)

                return users
            except Exception as e:
                raise e


async def crud_get_user(id: int) -> UserRead | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = select(User).where(User.id == id)
                result = await session.execute(stmt)
                query = result.first()
                data = query[0]
                user = {
                    "id": data.id,
                    "email": data.email,
                    "is_active": data.is_active,
                    "is_superuser": data.is_superuser,
                    "is_verified": data.is_verified
                }

                return user
            except Exception as e:
                raise e


async def crud_update_user(id: int, data: UserUpdate) -> None | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                hpw = get_password_hash(data.password)
                stmt = update(User).where(User.id == id).values(
                    email=data.email,
                    hashed_password=hpw,
                    is_active=data.is_active,
                    is_superuser=data.is_superuser,
                    is_verified=data.is_verified
                )
                await session.execute(stmt)
            except Exception as e:
                raise e


async def crud_update_user_email(id: int, email: str) -> None | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = update(User).where(User.id == id).values(
                    email=email
                )
                await session.execute(stmt)
            except Exception as e:
                raise e


async def crud_update_user_password(id: int, password: str) -> None | Exception:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                hpw = get_password_hash(password)
                stmt = update(User).where(User.id == id).values(
                    hashed_password=hpw
                )
                await session.execute(stmt)
            except Exception as e:
                raise e


async def crud_delete_user(id: int) -> None | Exception:
     async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = delete(User).where(User.id == id)
                await session.execute(stmt)
            except Exception as e:
                raise e


async def crud_add_user_server(data: ActiveServerCreate) -> None | Exception:
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

                user_server = ActiveServer()
                user_server.user_id = data.user_id
                user_server.server_id = data.server_id
                user_server.iso = data.iso
                user_server.ipv4 = data.ipv4
                user_server.ipv6 = data.ipv6
                user_server.start_at = data.start_at
                user_server.end_at = data.end_at
            except Exception as e:
                raise e


async def crud_get_user_servers(id: int) -> list[Row]:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = select(column("id")).select_from(ActiveServer).where(ActiveServer.user_id == id)
                result = await session.execute(stmt)
                user_servers_id = [row[0] for row in result.all()]
 
                stmt = select(Server).where(Server.id.in_(user_servers_id))
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


async def crud_get_user_server(user_id: int, server_id: int) -> Row:
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


async def crud_update_user_server(data: ActiveServerUpdate) -> None | Exception:
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


async def crud_delete_user_server(id: int) -> None | Exception:
     async with async_session_maker() as session:
        async with session.begin():
            try:
                stmt = delete(ActiveServer).where(ActiveServer.id == id)
                await session.execute(stmt)
            except Exception as e:
                raise e
