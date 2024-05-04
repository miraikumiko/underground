import subprocess
import libvirt
from libvirt import libvirtError
from mako.template import Template
from src.logger import logger
from src.server.models import Server
from src.server.schemas import ServerUpdate
from src.server.crud import crud_read_server, crud_update_server
from src.node.crud import crud_read_node


async def vps_install(server: Server, os: str):
    if os not in (
        "debian", "ubuntu", "fedora",
        "arch", "alpine", "gentoo",
        "freebsd", "openbsd", "netbsd"
    ):
        raise Exception("Invalid OS")

    node = await crud_read_node(server.node_id)

    with libvirt.open(f"qemu+ssh://{node.ip}/system") as conn:
        try:
            vps = conn.lookupByName(str(server.id))
            state, _ = vps.state()

            if state == libvirt.VIR_DOMAIN_RUNNING:
                vps.destroy()

            vps.undefine()
        except libvirtError:
            pass

    subprocess.Popen(f"ssh root@{node.ip} 'virt-install --name {server.id} --vcpus {server.cores} --memory {server.ram} --disk /var/lib/libvirt/images/{server.id}.qcow2,size={server.disk_size} --cdrom /opt/iso/{os}.iso --os-variant unknown --graphics vnc,listen={node.ip},port={server.vnc_port}'", shell=True)


async def vps_delete(node_ip: str, name: str):
    with libvirt.open(f"qemu+ssh://{node_ip}/system") as conn:
        vps = conn.lookupByName(name)

        try:
            vps.destroy()
        except libvirtError:
            pass

        try:
            vps.undefine()
        except libvirtError:
            pass

    await vps_delete_disk(node_ip, name)


async def vps_action(server_id: int, action: str) -> None:
    server = await crud_read_server(server_id)
    node = await crud_read_node(server.node_id)

    if server.active:
        with libvirt.open(f"qemu+ssh://{node.ip}/system") as conn:
            vps = conn.lookupByName(str(server_id))

            if action == "on":
                vps.create()
            elif action == "reboot":
                vps.reboot()
            elif action == "off":
                vps.destroy()
            elif action == "delete":
                await vps_delete(node.ip, str(server_id))
            else:
                raise Exception("Invalid action")


async def vps_status(server_id: int) -> str:
    server = await crud_read_server(server_id)
    node = await crud_read_node(server.node_id)

    with libvirt.open(f"qemu+ssh://{node.ip}/system") as conn:
        try:
            vps = conn.lookupByName(str(server_id))
            state, _ = vps.state()

            if state == libvirt.VIR_DOMAIN_RUNNING:
                return "on"
            elif state == libvirt.VIR_DOMAIN_REBOOT_SIGNAL:
                return "reboot"
            elif state == libvirt.VIR_DOMAIN_SHUTOFF:
                return "off"
            else:
                return "unknown"
        except libvirtError:
            return "uninstalled"
        except Exception as e:
            logger.error(e)
            return "unknown"


async def vps_create_disk(node_ip: str, name: str, disk_size: int, os: str):
    try:
        subprocess.run(f"ssh root@{node_ip} 'qemu-img create /var/lib/libvirt/images/{name}.qcow2 -f qcow2 {disk_size}G'")
    except FileExistsError:
        pass


async def vps_delete_disk(node_ip: str, name: str):
    try:
        subprocess.run(f"ssh root@{node_ip} 'rm -f /var/lib/libvirt/images/{name}.qcow2'")
    except FileNotFoundError:
        pass
