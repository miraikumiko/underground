import libvirt
from mako.template import Template
from src.logger import logger
from src.config import QEMU_PORT
from src.server.crud import (
    crud_read_server,
    crud_read_server_ips
)
from src.server.rpc import rpc_create_disk, rpc_get_available_cores_number


async def vps_create(server_id: int) -> str:
    try:
        server_addresses = await crud_read_server_ips()
        server = await crud_read_server(server_id)

        for server_address in server_addresses:
            available_cores = await rpc_get_available_cores_number(server_address)

            if available_cores <= server.cores:
                raise Exception("Doesn't have available cores")

            with libvirt.open(f"qemu+ssh:///{server_address}:{QEMU_PORT}") as conn:
                with open("src/server/xml/vps.xml", "r") as file:
                    template = Template(file.read())
                    xml = template.render(
                        server_id=server_id,
                        cores=server.cores,
                        ram=server.ram
                    )

                    conn.defineXML(xml)

                    await rpc_create_disk(server_address, str(server_id), server.disk_size)

                    return xml
    except Exception as e:
        logger.error(e)
        raise e


async def vps_delete(server_id: int):
    try:
        print(server_id)
    except Exception as e:
        logger.error(e)
        raise e


async def vps_action(server_id: int, action: str) -> None:
    try:
        server = await crud_read_server(server_id)

        if server.active:
            async with libvirt.open(f"qemu+ssh:///{server.ipv4}:{QEMU_PORT}") as conn:
                if action == "on":
                    conn.lookupByName(str(server_id)).create()
                elif action == "reboot":
                    conn.lookupByName(str(server_id)).reboot()
                elif action == "off":
                    conn.lookupByName(str(server_id)).destroy()
                else:
                    raise Exception("Invalid action")
    except Exception as e:
        logger.error(e)
        raise e


async def vps_status(server_id: int) -> str:
    try:
        server = await crud_read_server(server_id)

        with libvirt.open(f"qemu+ssh:///{server.ipv4}:{QEMU_PORT}") as conn:
            state, _ = conn.lookupByName(str(server_id)).state()

            if state == libvirt.VIR_DOMAIN_RUNNING:
                return "on"
            elif state == libvirt.VIR_DOMAIN_REBOOT_SIGNAL:
                return "reboot"
            elif state == libvirt.VIR_DOMAIN_SHUTOFF:
                return "off"
            else:
                raise Exception("Unknown status")
    except Exception as e:
        logger.error(e)
        raise e
