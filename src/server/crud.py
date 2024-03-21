from src.crud import (
    crud_create,
    crud_reads,
    crud_read,
    crud_update,
    crud_delete
)
from src.server.models import (
    Server,
    ActiveServer,
    ServerIP
)
from src.server.schemas import (
    ServerCreate,
    ServerRead,
    ServerUpdate,
    ActiveServerCreate,
    ActiveServerRead,
    ActiveServerUpdate,
    ServerIPRead
)


async def crud_create_server(schema: ServerCreate) -> int:
    server_id = await crud_create(Server, schema)

    return server_id


async def crud_read_servers() -> list[ServerRead]:
    servers = await crud_reads(Server)

    return servers


async def crud_read_server(server_id: int) -> ServerRead:
    server = await crud_read(Server, attr1=Server.id, attr2=server_id)

    return server


async def crud_update_server(schema: ServerUpdate, server_id: int) -> None:
    await crud_update(Server, schema, attr1=Server.id, attr2=server_id)


async def crud_delete_server(server_id: int) -> None:
    await crud_delete(Server, attr1=Server.id, attr2=server_id)


async def crud_create_active_server(schema: ActiveServerCreate) -> int:
    active_server_id = await crud_create(ActiveServer, schema)

    return active_server_id


async def crud_read_active_servers(user_id: int = None) -> list[ActiveServerRead]:
    if user_id is not None:
        active_servers = await crud_reads(ActiveServer, attr1=ActiveServer.user_id, attr2=user_id)
    else:
        active_servers = await crud_reads(ActiveServer)

    return active_servers


async def crud_read_active_server(active_server_id: int) -> ActiveServerRead:
    active_server = await crud_read(ActiveServer, attr1=ActiveServer.id, attr2=active_server_id)

    return active_server


async def crud_update_active_server(schema: ActiveServerUpdate, active_server_id: int) -> None:
    await crud_update(ActiveServer, schema, attr1=ActiveServer.id, attr2=active_server_id)


async def crud_delete_active_server(active_server_id: int) -> None:
    await crud_delete(ActiveServer, attr1=ActiveServer.id, attr2=active_server_id)


async def crud_delete_active_servers(user_id: int) -> None:
    await crud_delete(ActiveServer, attr1=ActiveServer.user_id, attr2=user_id)


async def crud_read_server_ips() -> list[ServerIPRead]:
    server_ips = await crud_reads(ServerIP)

    return server_ips
