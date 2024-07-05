import subprocess
import libvirt
from libvirt import libvirtError
from src.logger import logger
from src.config import PRODUCTS
from src.server.models import Server
from src.server.schemas import ServerUpdate
from src.server.crud import crud_read_server, crud_update_server
from src.node.crud import crud_read_node


async def vps_install(server: Server, os: str):
    if os not in ("debian", "arch", "alpine", "gentoo", "freebsd", "openbsd"):
        raise ValueError("Invalid OS")

    node = await crud_read_node(server.node_id)

    cores = PRODUCTS["vps"][str(server.vps_id)]["cores"]
    ram = PRODUCTS["vps"][str(server.vps_id)]["ram"]
    disk_size = PRODUCTS["vps"][str(server.vps_id)]["disk_size"]

    with libvirt.open(f"qemu+ssh://{node.ip}/system") as conn:
        try:
            vps = conn.lookupByName(str(server.id))
            state, _ = vps.state()

            if state == libvirt.VIR_DOMAIN_RUNNING:
                vps.destroy()

            vps.undefine()
        except libvirtError:
            pass

    subprocess.Popen(f"ssh root@{node.ip} 'virt-install --name {server.id} --vcpus {cores} --memory {ram * 1000} --disk /var/lib/libvirt/images/{server.id}.qcow2,size={disk_size} --cdrom /opt/iso/{os}.iso --os-variant unknown --graphics vnc,listen={node.ip},port={server.vnc_port}'", shell=True)


async def vps_delete(node_ip: str, name: str):
    with libvirt.open(f"qemu+ssh://{node_ip}/system") as conn:
        try:
            vps = conn.lookupByName(name)
            vps.destroy()
            vps.undefine()
        except libvirtError:
            pass

    await vps_delete_disk(node_ip, name)


async def vps_action(server_id: int) -> None:
    server = await crud_read_server(server_id)
    node = await crud_read_node(server.node_id)

    if server.is_active:
        with libvirt.open(f"qemu+ssh://{node.ip}/system") as conn:
            try:
                vps = conn.lookupByName(str(server_id))
                state, _ = vps.state()

                if state == libvirt.VIR_DOMAIN_SHUTOFF:
                    vps.create()
                else:
                    vps.destroy()
            except:
              pass


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


async def vps_upgrade(server_id: int, vps_id: int) -> None:
    server = await crud_read_server(server_id)
    node = await crud_read_node(server.node_id)

    if server.is_active:
        with libvirt.open(f"qemu+ssh://{node.ip}/system") as conn:
            vps = conn.lookupByName(str(server_id))

            vps.destroy()

            if PRODUCTS["vps"][vps_id]["cores"] > server.cores:
                vps.setVcpu(cores)

            if PRODUCTS["vps"][vps_id]["ram"] > server.ram:
                vps.setMemory(ram)

            if PRODUCTS["vps"][vps_id]["disk_size"] > server.disk_size:
                subprocess.run(f"ssh root@{node.ip} 'qemu-img resize /var/lib/libvirt/images/{server_id}.qcow2 {PRODUCTS['vps'][str(vps_id)]['disk_size']}G'")
