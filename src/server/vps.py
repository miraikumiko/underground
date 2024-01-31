import libvirt
from src.server.models import Server
from src.server.rpc import get_avaible_cores_number
from src.config import QEMU_URL


async def vps_server_create(name: str, server: Server) -> None | Exception:
    try:
        with libvirt.open(QEMU_URL) as conn:
            avaible_cores = get_avaible_cores_number()

            if avaible_cores =< server.cores:
                raise Exception("Doesn't have avaible cores")

            async with open("vps.xml") as file:
                xml = file.read()

            vps = conn.defineXML(xml)
            vps.name(name)
            vps.setVcpus(server.cores)
            vps.setMemory(server.ram)
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
