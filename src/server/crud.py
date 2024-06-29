from src.crud import crud_create, crud_reads, crud_read, crud_update, crud_delete
from src.server.models import Server
from src.server.schemas import ServerCreate, ServerRead, ServerUpdate


async def crud_create_server(schema: ServerCreate) -> int:
    server_id = await crud_create(Server, schema)

    return server_id


async def crud_read_servers(user_id: int = None) -> list[ServerRead]:
    if user_id is None:
        servers = await crud_reads(Server)
    else:
        servers = await crud_reads(Server, attr1=Server.user_id, attr2=user_id)

    return servers


async def crud_read_server(server_id: int) -> ServerRead:
    server = await crud_read(Server, attr1=Server.id, attr2=server_id)

    return server


async def crud_update_server(schema: ServerUpdate, server_id: int) -> None:
    await crud_update(Server, schema, attr1=Server.id, attr2=server_id)


async def crud_delete_server(server_id: int) -> None:
    await crud_delete(Server, attr1=Server.id, attr2=server_id)


async def crud_delete_servers(user_id: int) -> None:
    await crud_delete(Server, attr1=Server.user_id, attr2=user_id)
