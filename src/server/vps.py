import libvirt
from mako.template import Template
from src.server.models import ActiveServer
from src.server.crud import crud_get_server
from src.server.rpc import get_avaible_cores_number
from src.config import QEMU_URL


async def vps_server_create(active_server: ActiveServer) -> str | Exception:
    try:
        with libvirt.open(QEMU_URL) as conn:
            avaible_cores = await get_avaible_cores_number()

            server = await crud_get_server(active_server.server_id)

            if avaible_cores <= server.cores:
                raise Exception("Doesn't have avaible cores")

            with open("src/server/xml/vps.xml", "r") as file:
                template = Template(file.read())
                xml = template.render(
                    active_server_id=active_server.id,
                    cores=server.cores,
                    ram=server.ram
                )

                conn.defineXML(xml)

                return xml
    except Exception as e:
        raise e


async def vps_server_on(name: str) -> None | Exception:
    try:
        async with libvirt.open(QEMU_URL) as conn:
            conn.lookupByName(name).create()
    except Exception as e:
        raise e


async def vps_server_reboot(name: str) -> None | Exception:
    try:
        async with libvirt.open(QEMU_URL) as conn:
            conn.lookupByName(name).reboot()
    except Exception as e:
        raise e


async def vps_server_off(name: str) -> None | Exception:
    try:
        async with libvirt.open(QEMU_URL) as conn:
            conn.lookupByName(name).destroy()
    except Exception as e:
        raise e


async def vps_server_status(name: str) -> str | Exception:
    async with libvirt.open(QEMU_URL) as conn:
        try:
            state, _ = conn.lookupByName(name).state()

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
