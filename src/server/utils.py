from os import makedirs
from datetime import datetime, timedelta
from fastapi import UploadFile
from src.mail import sendmail
from src.utils import err_catch
from src.logger import logger
from src.server.schemas import ServerUpdate
from src.server.crud import crud_read_servers, crud_update_server, crud_delete_server
from src.server.vps import vps_delete, vps_action
from src.user.crud import crud_read_user


@err_catch
async def upload_iso(user_id: int, iso: UploadFile) -> None:
    iso_path = f"/var/lib/libvirt/iso/{user_id}"

    makedirs(iso_path, exist_ok=True)

    with open(f"{iso_path}/{iso.filename}", "wb") as file:
        file.write(await iso.read())


async def servers_expired_check():
    servers = await crud_read_servers()

    for server in servers:
        if datetime.now() >= server.end_at + timedelta(days=7):
            user = await crud_read_user(server.user_id)
            subject = "[Notification] Your VPS has been expired and deleted"
            body = "Your VPS has been expired and deleted."

            await sendmail(subject, body, user.email)
            await crud_delete_server(server.id)
            await vps_delete(server.id)

            logger.info(f"Active server with id {server.id} has been expired and deleted")
        elif datetime.now() >= server.end_at:
            user = await crud_read_user(server.user_id)
            subject = "[Notification] VPS has been expired"
            body = "Your VPS has been expired. Please, pay the billing, if you want to continue using it."

            await sendmail(subject, body, user.email)
            await crud_update_server(ServerUpdate(**{"active": False}), server.id)
            await vps_action(server.id, "off")

            logger.info(f"Active server with id {server.id} has been expired")
