import libvirt
from mako.template import Template
from src.config import QEMU_PORT
from src.server.crud import (
    crud_read_server,
    crud_read_active_server,
    crud_read_server_ips
)
from src.server.rpc import rpc_create_disk, rpc_get_available_cores_number


async def vps_create(active_server_id: int, server_id: int) -> str:
    try:
        server_addresses = await crud_read_server_ips()
        server = await crud_read_server(server_id)

        for server_address in server_addresses:
            available_cores = await rpc_get_available_cores_number(server_address.ip)

            if available_cores <= server.cores:
                raise Exception("Doesn't have available cores")

            with libvirt.open(f"qemu+ssh:///{server_address.ip}:{QEMU_PORT}") as conn:
                with open("src/server/xml/vps.xml", "r") as file:
                    template = Template(file.read())
                    xml = template.render(
                        active_server_id=active_server_id,
                        cores=server.cores,
                        ram=server.ram
                    )

                    conn.defineXML(xml)

                    await rpc_create_disk(server_address.ip, str(active_server_id), server.disk_size)

                    return xml
    except Exception as e:
        raise e


async def vps_delete(active_server_id: int):
    print(active_server_id)


async def vps_on(active_server_id: int) -> None:
    try:
        active_server = await crud_read_active_server(active_server_id)

        if active_server.active:
            async with libvirt.open(f"qemu+ssh:///{active_server.ipv4}:{QEMU_PORT}") as conn:
                conn.lookupByName(str(active_server_id)).create()
    except Exception as e:
        raise e


async def vps_reboot(active_server_id: int) -> None:
    try:
        active_server = await crud_read_active_server(active_server_id)

        if active_server.active:
            async with libvirt.open(f"qemu+ssh:///{active_server.ipv4}:{QEMU_PORT}") as conn:
                conn.lookupByName(str(active_server_id)).reboot()
    except Exception as e:
        raise e


async def vps_off(active_server_id: int) -> None:
    try:
        active_server = await crud_read_active_server(active_server_id)

        if active_server.active:
            async with libvirt.open(f"qemu+ssh:///{active_server.ipv4}:{QEMU_PORT}") as conn:
                conn.lookupByName(str(active_server_id)).destroy()
    except Exception as e:
        raise e


async def vps_status(active_server_id: int) -> str:
    try:
        active_server = await crud_read_active_server(active_server_id)

        with libvirt.open(f"qemu+ssh:///{active_server.ipv4}:{QEMU_PORT}") as conn:
            state, _ = conn.lookupByName(str(active_server_id)).state()

            if state == libvirt.VIR_DOMAIN_RUNNING:
                return "on"
            elif state == libvirt.VIR_DOMAIN_REBOOT_SIGNAL:
                return "reboot"
            elif state == libvirt.VIR_DOMAIN_SHUTOFF:
                return "off"
            else:
                raise Exception("Unknown status")
    except Exception as e:
        raise e
