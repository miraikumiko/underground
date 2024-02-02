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

            xml = f"""
            <domain type='kvm'>
                <name>{name}</name>
                <memory unit='GiB'>{server.ram}</memory>
                <vcpu placement='static'>{server.cores}</vcpu>
                <devices>
                    <emulator>/usr/bin/qemu-system-x86_64</emulator>
                    <disk type='file' device='cdrom'>
                        <driver name='qemu' type='raw'/>
                        <source file='/var/lib/libvirt/iso/alpine-standard-3.19.0-x86_64.iso'/>
                        <target dev='sdb' bus='sata'/>
                        <readonly/>
                        <boot order='1'/>
                        <address type='drive' controller='0' bus='0' target='0' unit='1'/>
                    </disk>
                    <disk type='file' device='disk'>
                        <driver name='qemu' type='qcow2' discard='unmap'/>
                        <source file='/var/lib/libvirt/images/{name}.qcow2'/>
                        <target dev='sda' bus='sata'/>
                        <boot order='2'/>
                        <address type='drive' controller='0' bus='0' target='0' unit='0'/>
                    </disk>
                    <interface type='network'>
                        <mac address='52:54:00:4e:31:f9'/>
                        <source network='default'/>
                        <model type='e1000e'/>
                        <address type='pci' domain='0x0000' bus='0x01' slot='0x00' function='0x0'/>
                    </interface>
                    <graphics type='vnc' port='-1' autoport='yes'>
                        <listen type='address'/>
                    </graphics>
                </devices>
            </domain>
            """

            vps = conn.defineXML(xml)
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
