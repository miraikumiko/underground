from datetime import datetime, timedelta
from src.database import r
from src.mail import sendmail
from src.logger import logger
from src.server.schemas import IPUpdate
from src.server.crud import (
    crud_read_servers, crud_update_server, crud_delete_server,
    crud_update_ipv4
)
from src.server.vps import vps_delete, vps_action
from src.node.schemas import NodeUpdate
from src.node.crud import crud_read_node, crud_update_node
from src.user.crud import crud_read_user


async def servers_expired_check():
    servers = await crud_read_servers()

    for server in servers:
        if server.end_at + timedelta(days=3) <= datetime.now():
            user = await crud_read_user(server.user_id)
            subject = "[Notification] Your VPS has been expired and deleted"
            body = "Your VPS has been expired and deleted."

            await sendmail(subject, body, user.email)
            await crud_delete_server(server.id)
            await vps_delete(server.id)

            logger.info(f"Active server with id {server.id} has been expired and deleted")
        elif server.end_at <= datetime.now():
            user = await crud_read_user(server.user_id)
            subject = "[Notification] VPS has been expired"
            body = "Your VPS has been expired. Please, pay the billing, if you want to continue using it."

            await sendmail(subject, body, user.email)

            logger.info(f"Active server with id {server.id} has been expired")

        if not server.active:
            is_expired = await r.get(f"inactive_server:{server.id}")

            if is_expired is None:
                node = await crud_read_node(server.node_id)

                cores = node.cores_available + server.cores
                ram = node.ram_available + server.ram
                disk_size = node.disk_size_available + server.disk_size

                if cores > node.cores:
                    cores = node.cores

                if ram > node.ram:
                    ram = node.ram

                if disk_size > node.disk_size:
                    disk_size = node.disk_size

                node_schema = NodeUpdate(
                    cores_available=cores,
                    ram_available=ram,
                    disk_size_available=disk_size
                )
                ipv4_schema = IPUpdate(available=True)

                await crud_update_node(node_schema, server.node_id)
                await crud_update_ipv4(ipv4_schema, server.ipv4)
                await crud_delete_server(server.id)
