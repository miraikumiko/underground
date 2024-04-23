import libvirt
from libvirt import libvirtError
from mako.template import Template
from src.logger import logger
from src.server.schemas import ServerUpdate
from src.server.crud import crud_read_server, crud_update_server, crud_read_nodes
from src.server.rpc import rpc_create_disk, rpc_delete_disk


async def vps_create(server_id: int, os: str):
    try:
        server = await crud_read_server(server_id)
        nodes = await crud_read_nodes(server.cores, server.ram, server.disk_size)

        if not nodes:
            raise Exception("Doesn't have available nodes")

        node = nodes[0]

        with libvirt.open(f"qemu+ssh://{node.ip}/system") as conn:
            with open("src/server/xml/vps.xml", "r") as file:
                template = Template(file.read())
                xml = template.render(
                    server_id=server.id,
                    cores=server.cores,
                    ram=server.ram
                )

                conn.defineXML(xml)

                await rpc_create_disk(node.ip, str(server_id), server.disk_size)
                await crud_update_server(ServerUpdate(node_id=node.id), server_id)
    except Exception as e:
        logger.error(e)
        raise e


async def vps_delete(server_id: int):
    try:
        await rpc_delete_disk("", str(server_id))
    except Exception as e:
        logger.error(e)
        raise e


async def vps_action(server_id: int, action: str) -> None:
    try:
        server = await crud_read_server(server_id)

        if server.active:
            async with libvirt.open(f"qemu+ssh://{server.ipv4}/system") as conn:
                vps = conn.lookupByName(str(server_id))

                if action == "on":
                    vps.create()
                elif action == "reboot":
                    vps.reboot()
                elif action == "off":
                    vps.destroy()
                elif action == "delete":
                    vps.destroy()
                    await vps_delete(str(server_id))
                else:
                    raise Exception("Invalid action")
    except Exception as e:
        logger.error(e)
        raise e


async def vps_status(server_id: int) -> str:
    server = await crud_read_server(server_id)

    with libvirt.open(f"qemu+ssh://{server.ipv4}/system") as conn:
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
