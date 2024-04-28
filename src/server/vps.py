import os
import libvirt
from libvirt import libvirtError
from mako.template import Template
from src.logger import logger
from src.server.schemas import ServerUpdate
from src.server.crud import crud_read_server, crud_update_server
from src.node.crud import crud_read_node


async def vps_create_disk(node_ip: str, name: str, disk_size: float):
    try:
        os.system(f"ssh root@{node_ip} 'qemu-img create /var/lib/libvirt/images/{name}.qcow2 -f qcow2 {disk_size}G'")
    except Exception as e:
        logger.error(e)
        raise e


async def vps_delete_disk(node_ip: str, name: str):
    try:
        os.system(f"ssh root@{node_ip} 'rm -f /var/lib/libvirt/images/{name}.qcow2'")
    except Exception as e:
        logger.error(e)
        raise e


async def vps_create(server_id: int, os: str):
    try:
        server = await crud_read_server(server_id)
        node = await crud_read_node(server.node_id)

        with libvirt.open(f"qemu+ssh://{node.ip}/system") as conn:
            with open("src/server/xml/vps.xml", "r") as file:
                template = Template(file.read())
                xml = template.render(
                    name=server.id,
                    cores=server.cores,
                    ram=server.ram
                )

                conn.defineXML(xml)

        await vps_create_disk(node.ip, str(server_id), server.disk_size)
    except Exception as e:
        logger.error(e)
        raise e


async def vps_delete(node_ip: str, name: str):
    try:
        async with libvirt.open(f"qemu+ssh://{node_ip}/system") as conn:
            vps = conn.lookupByName(name)

            vps.destroy()
            vps.undefine()

        await vps_delete_disk(node_ip, name)
    except Exception as e:
        logger.error(e)
        raise e


async def vps_action(server_id: int, action: str) -> None:
    try:
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
                    await vps_delete(str(server_id))
                else:
                    raise Exception("Invalid action")
    except Exception as e:
        logger.error(e)
        raise e


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
