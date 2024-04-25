from datetime import datetime, timedelta
from src.database import r
from src.mail import sendmail
from src.logger import logger
from src.server.schemas import NodeUpdate
from src.server.crud import (
    crud_read_servers,
    crud_update_server,
    crud_delete_server,
    crud_read_node,
    crud_update_node
)
from src.server.vps import vps_delete, vps_action
from src.user.crud import crud_read_user


async def servers_expired_check():
    servers = await crud_read_servers()

    for server in servers:
        if server.end_at + timedelta(days=7) <= datetime.now():
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
            is_expired = await r.get(f"inactive_server:{server_id}")

            if is_expired is None:
                node = await crud_read_node(server.node_id)

                node_schema = NodeUpdate(
                    cores_available=(node.cores_available + server.cores),
                    ram_available=(node.ram_available + server.ram),
                    disk_size_available=(node.disk_size_available + server.disk_size)
                )

                await crud_update_node(node_schema, server.node_id)
                await crud_delete_server(server.id)
