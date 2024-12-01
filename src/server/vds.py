import subprocess
import libvirt
from libvirt import libvirtError
from src.logger import logger
from src.server.schemas import ServerRead
from src.server.crud import crud_read_server
from src.node.crud import crud_read_node
from src.payment.crud import crud_read_vds


async def vds_install(server: ServerRead, os: str) -> None:
    if os not in ("debian", "arch", "alpine", "gentoo", "freebsd", "openbsd"):
        raise ValueError("Invalid OS")

    node = await crud_read_node(server.node_id)
    vds = await crud_read_vds(server.vds_id)

    try:
        with libvirt.open(f"qemu+ssh://{node.ip}/system") as conn:
            vds = conn.lookupByName(str(server.id))
            state, _ = vds.state()

            if state == libvirt.VIR_DOMAIN_RUNNING:
                vds.destroy()

            vds.undefine()
    except Exception as e:
        logger.error(e)

    subprocess.Popen(f"""ssh root@{node.ip} 'virt-install \
        --name {server.id} \
        --vcpus {vds.cores} \
        --memory {vds.ram * 1000} \
        --disk /var/lib/libvirt/images/{server.id}.qcow2,size={vds.disk_size} \
        --cdrom /opt/iso/{os}.iso \
        --os-variant unknown \
        --graphics vnc,listen={node.ip},port={server.vnc_port}'""", shell=True)


async def vds_delete(node_ip: str, name: str) -> None:
    try:
        with libvirt.open(f"qemu+ssh://{node_ip}/system") as conn:
            vds = conn.lookupByName(name)
            vds.destroy()
            vds.undefine()
    except Exception as e:
        logger.error(e)

    await vds_delete_disk(node_ip, name)


async def vds_action(server_id: int) -> None:
    server = await crud_read_server(server_id)
    node = await crud_read_node(server.node_id)

    if server.is_active:
        try:
            with libvirt.open(f"qemu+ssh://{node.ip}/system") as conn:
                vds = conn.lookupByName(str(server_id))
                state, _ = vds.state()

                if state == libvirt.VIR_DOMAIN_SHUTOFF:
                    vds.create()
                else:
                    vds.destroy()
        except Exception as e:
            logger.error(e)


async def vds_status(server_id: int) -> str:
    server = await crud_read_server(server_id)
    node = await crud_read_node(server.node_id)

    try:
        with libvirt.open(f"qemu+ssh://{node.ip}/system") as conn:
            try:
                vds = conn.lookupByName(str(server_id))
                state, _ = vds.state()

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
    except Exception as e:
        logger.error(e)
        return "unknown"


async def vds_create_disk(node_ip: str, name: str, disk_size: int) -> None:
    try:
        subprocess.run(f"""ssh root@{node_ip} 'qemu-img create /var/lib/libvirt/images/{name}.qcow2 \
            -f qcow2 {disk_size}G'""")
    except FileExistsError:
        pass


async def vds_delete_disk(node_ip: str, name: str) -> None:
    try:
        subprocess.run(f"ssh root@{node_ip} 'rm -f /var/lib/libvirt/images/{name}.qcow2'")
    except FileNotFoundError:
        pass


async def vds_upgrade(server_id: int, vds_id: int) -> None:
    server = await crud_read_server(server_id)
    node = await crud_read_node(server.node_id)

    if server.is_active:
        try:
            with libvirt.open(f"qemu+ssh://{node.ip}/system") as conn:
                vds = conn.lookupByName(str(server_id))

                vds.destroy()

                vds = await crud_read_vds(vds_id)

                if vds.cores > server.cores:
                    vds.setVcpu(vds.cores)

                if vds.ram > server.ram:
                    vds.setMemory(vds.ram)

                if vds.disk_size > server.disk_size:
                    subprocess.run(f"""ssh root@{node.ip} 'qemu-img \
                        resize /var/lib/libvirt/images/{server_id}.qcow2 {vds.disk_size}G'""")
        except Exception as e:
            logger.error(e)
