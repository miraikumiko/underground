from src.crud import (
    crud_create,
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
    ServerDelete,
    ActiveServerCreate,
    ActiveServerRead,
    ActiveServerUpdate,
    ActiveServerDelete,
    ServerIPRead
)


async def crud_create_server(Schema: ServerCreate) -> int:
    id = await crud_create(Server, Schema)

    return id


async def crud_read_servers() -> list[ServerRead]:
    servers = await crud_read(Server, all=True)

    return servers


async def crud_read_server(Schema: ServerRead) -> ServerRead:
    server = await crud_read(Server, Schema)

    return server


async def crud_update_server(Schema: ServerUpdate) -> None:
    await crud_update(Server, Schema)


async def crud_delete_server(Schema: ServerDelete) -> None:
    await crud_delete(Server, Schema)


async def crud_create_active_server(Schema: ActiveServerCreate) -> int:
    id = await crud_create(ActiveServer, Schema)

    return id


async def crud_read_active_servers(Schema: ActiveServerRead) -> list[ActiveServerRead]:
    if Schema.id is None:
        active_servers = await crud_read(
            ActiveServer,
            Schema,
            attr1=ActiveServer.user_id,
            attr2=Schema.user_id,
            all=True
        )
    else:
        active_servers = await crud_read(ActiveServer, Schema, all=True)

    return active_servers


async def crud_read_active_server(Schema: ActiveServerRead) -> ActiveServerRead:
    if Schema.id is None:
        active_server = await crud_read(
            ActiveServer,
            Schema,
            attr1=ActiveServer.user_id,
            attr2=Schema.user_id
        )
    else:
        active_server = await crud_read(ActiveServer, Schema)

    return active_server


async def crud_update_active_server(Schema: ActiveServerUpdate) -> None:
    await crud_update(ActiveServer, Schema)


async def crud_delete_active_server(Schema: ActiveServerDelete) -> None:
    await crud_delete(ActiveServer, Schema)


async def crud_read_server_ips() -> list[ServerIPRead]:
    server_ips = await crud_read(ServerIP)

    return server_ips
