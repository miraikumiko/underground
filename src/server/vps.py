import libvirt
from mako.template import Template
from src.config import QEMU_PORT
from src.server.models import ActiveServer
from src.server.crud import (
    crud_get_server,
    crud_get_active_server,
    crud_get_server_ips
)
from src.server.rpc import rpc_create_disk, rpc_get_avaible_cores_number


async def vps_server_create(active_server: ActiveServer) -> str:
    try:
        server_addresses = await crud_get_server_ips()

        for ip in server_addresses.ip:
            avaible_cores = await rpc_get_avaible_cores_number(ip)

            if avaible_cores <= server.cores:
                raise Exception("Doesn't have avaible cores")

            with libvirt.open(f"qemu+ssh:///{ip}:{QEMU_PORT}") as conn:
                server = await crud_get_server(active_server.server_id)

                with open("src/server/xml/vps.xml", "r") as file:
                    template = Template(file.read())
                    xml = template.render(
                        active_server_id=active_server.id,
                        cores=server.cores,
                        ram=server.ram
                    )

                    conn.defineXML(xml)

                    rpc_create_disk(ip, str(active_server.id), server.disk_size)

                    return xml
    except Exception as e:
        raise e


async def vps_server_on(active_server_id: int) -> None:
    try:
        active_server = await crud_get_active_server({"id": active_server_id})

        async with libvirt.open(f"qemu+ssh:///{active_server.ip}:{QEMU_PORT}") as conn:
            conn.lookupByName(str(active_server_id)).create()
    except Exception as e:
        raise e


async def vps_server_reboot(active_server_id: int) -> None:
    try:
        active_server = await crud_get_active_server({"id": active_server_id})

        async with libvirt.open(f"qemu+ssh:///{active_server.ip}:{QEMU_PORT}") as conn:
            conn.lookupByName(str(active_server_id)).reboot()
    except Exception as e:
        raise e


async def vps_server_off(active_server_id: int) -> None:
    try:
        active_server = await crud_get_active_server({"id": active_server_id})

        async with libvirt.open(f"qemu+ssh:///{active_server.ip}:{QEMU_PORT}") as conn:
            conn.lookupByName(str(active_server_id)).destroy()
    except Exception as e:
        raise e


async def vps_server_status(active_server_id: int) -> str:
    try:
        active_server = await crud_get_active_server({"id": active_server_id})

        with libvirt.open(f"qemu+ssh:///{active_server.ip}:{QEMU_PORT}") as conn:
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
