from fastapi import HTTPException
from ipaddress import IPv4Address, IPv4Network
from datetime import datetime, timedelta, UTC
from src.database import r
from src.config import VDS_EXPIRED_DAYS, SUBNET_IPV4
from src.logger import logger
from src.user.models import User
from src.server.schemas import ServerCreate
from src.server.crud import crud_create_server, crud_read_servers, crud_delete_server
from src.server.vds import vds_delete
from src.node.schemas import NodeUpdate
from src.node.crud import crud_read_node, crud_read_nodes, crud_update_node
from src.payment.crud import crud_read_vds


async def request_vds(product_id: int, user: User, is_active: bool = False) -> int:
    # Validate product id
    vds = await crud_read_vds(product_id)

    if not vds:
        raise Exception("Bad Request|This product doesn't exist")

    servers = await crud_read_servers()

    # Check availability of IPv4
    if vds.ipv4:
        if servers:
            server_ipv4s = [IPv4Address(server.ipv4) for server in servers if server.ipv4]
            available_ipv4s = [ipv4 for ipv4 in IPv4Network(SUBNET_IPV4) if ipv4 not in server_ipv4s]

            if not available_ipv4s:
                logger.warn(f"Haven't available IPv4 for new vds with id {product_id} for {user.username}")
                raise HTTPException(503, "d|We haven't available resources")

    # Check availability of resources
    nodes = await crud_read_nodes(vds.cores, vds.ram, vds.disk_size)

    if not nodes:
        logger.warn(f"Haven't available resources for new vds with id {product_id} for {user.username}")
        raise HTTPException(503, "d|We haven't available resources")

    node = nodes[0]

    # Reservation port for VNC
    vnc_port = 5900

    if servers:
        up = [server.vnc_port for server in servers if server.node_id == node.id]
        while vnc_port in up:
            vnc_port += 1

    # Registration of new server
    server_schema = ServerCreate(
        vnc_port=vnc_port,
        ipv4=None,
        ipv6=None,
        start_at=datetime.now(UTC),
        end_at=datetime.now() + timedelta(days=31),
        is_active=False,
        vds_id=product_id,
        node_id=node.id,
        user_id=user.id
    )

    if is_active:
        server_schema.is_active = True

    node_schema = NodeUpdate(
        cores_available=(node.cores_available - vds.cores),
        ram_available=(node.ram_available - vds.ram),
        disk_size_available=(node.disk_size_available - vds.disk_size)
    )

    await crud_update_node(node_schema, node.id)
    server_id = await crud_create_server(server_schema)

    return server_id


async def servers_expired_check():
    servers = await crud_read_servers()

    for server in servers:
        if server.end_at + timedelta(days=VDS_EXPIRED_DAYS) <= datetime.now():
            node = await crud_read_node(server.node_id)

            await crud_delete_server(server.id)
            await vds_delete(node.ip, str(server.id))

            logger.info(f"Server {server.id} has been expired and deleted")
        elif server.end_at <= datetime.now():
            logger.info(f"Server {server.id} has been expired")

        if not server.is_active:
            is_expired = await r.get(f"inactive_server:{server.id}")

            if not is_expired:
                node = await crud_read_node(server.node_id)
                vds = await crud_read_vds(server.vds_id)
                cores = vds.cores
                ram = vds.ram
                disk_size = vds.disk_size

                if vds.cores > node.cores:
                    cores = node.cores
                if vds.ram > node.ram:
                    ram = node.ram
                if vds.disk_size > node.disk_size:
                    disk_size = node.disk_size

                node_schema = NodeUpdate(
                    cores_available=cores,
                    ram_available=ram,
                    disk_size_available=disk_size
                )

                await crud_update_node(node_schema, server.node_id)
                await crud_delete_server(server.id)

                logger.info(f"Server {server.id} has been deleted")
