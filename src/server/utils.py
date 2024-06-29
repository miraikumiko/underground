from datetime import datetime, timedelta
from src.database import r
from src.config import PRODUCTS
from src.logger import logger
from src.server.schemas import IPUpdate
from src.server.crud import crud_read_servers, crud_update_server, crud_delete_server
from src.server.vps import vps_delete, vps_action
from src.node.schemas import NodeUpdate
from src.node.crud import crud_read_node, crud_update_node
from src.user.crud import crud_read_user


async def servers_expired_check():
    servers = await crud_read_servers()

    for server in servers:
        if server.end_at + timedelta(days=3) <= datetime.now():
            user = await crud_read_user(server.user_id)

            await crud_delete_server(server.id)
            await vps_delete(server.id)

            logger.info(f"Server {server.id} has been expired and deleted")
        elif server.end_at <= datetime.now():
            user = await crud_read_user(server.user_id)

            logger.info(f"Server {server.id} has been expired")

        if not server.is_active:
            is_expired = await r.get(f"inactive_server:{server.id}")

            if is_expired is None:
                node = await crud_read_node(server.node_id)

                cores = node.cores_available + PRODUCTS["vps"][str(server.vps_id)]["cores"]
                ram = node.ram_available + PRODUCTS["vps"][str(server.vps_id)]["ram"]
                disk_size = node.disk_size_available + PRODUCTS["vps"][str(server.vps_id)]["disk_size"]

                if cores > node.cores: cores = node.cores
                if ram > node.ram: ram = node.ram
                if disk_size > node.disk_size: disk_size = node.disk_size

                node_schema = NodeUpdate(
                    cores_available=cores,
                    ram_available=ram,
                    disk_size_available=disk_size
                )

                await crud_update_node(node_schema, server.node_id)
                await crud_delete_server(server.id)

                logger.info(f"Server {server.id} has been deleted")
