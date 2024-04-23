from src.crud import crud_create, crud_reads, crud_read, crud_update, crud_delete
from src.server.models import Server, Node, IPv4, IPv6
from src.server.schemas import (
    ServerCreate,
    ServerRead,
    ServerUpdate,
    NodeCreate,
    NodeRead,
    NodeUpdate,
    IPv4Addr,
    IPv6Addr
)


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


async def crud_create_node(schema: NodeCreate) -> int:
    node_id = await crud_create(Node, schema)

    return node_id


async def crud_read_nodes(
    cores_available: int = None,
    ram_available: int = None,
    disk_size_available: int = None
) -> list[NodeRead]:
    nodes = await crud_reads(Node)

    if nodes:
        if cores_available is not None:
            nodes = [node for node in nodes if node.cores_available >= cores_available]

        if ram_available is not None:
            nodes = [node for node in nodes if node.ram_available >= ram_available]

        if disk_size_available is not None:
            nodes = [node for node in nodes if node.disk_size_available >= disk_size_available]

    return nodes


async def crud_read_node(node_id: int) -> NodeRead:
    node = await crud_read(Node, attr1=Node.id, attr2=node_id)

    return node


async def crud_update_node(schema: NodeUpdate, node_id: int) -> None:
    await crud_update(Node, schema, attr1=Node.id, attr2=node_id)


async def crud_delete_node(node_id: int) -> None:
    await crud_delete(Node, attr1=Node.id, attr2=node_id)


async def crud_read_ipv4s(available: bool = None) -> list[IPv4Addr]:
    if available is None:
        ipv4s = await crud_reads(IPv4)
    else:
        ipv4s = await crud_reads(IPv4, attr1=IPv4.available, attr2=available)

    return ipv4s


async def crud_update_ipv4(schema: IPv4Addr, ip: str) -> None:
    await crud_update(IPv4, schema, attr1=IPv4.ip, attr2=ip)


async def crud_read_ipv6s(available: bool = None) -> list[IPv6Addr]:
    if available is None:
        ipv6s = await crud_reads(IPv6)
    else:
        ipv6s = await crud_reads(IPv6, attr1=IPv6.available, attr2=available)

    return ipv6s


async def crud_update_ipv6(schema: IPv6Addr, ip: str) -> None:
    await crud_update(IPv6, schema, attr1=IPv6.ip, attr2=ip)
