from src.crud import crud_create, crud_reads, crud_read, crud_update, crud_delete
from src.node.models import Node
from src.node.schemas import NodeCreate, NodeRead, NodeUpdate


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
