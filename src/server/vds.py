import subprocess
import libvirt
from xml.etree import ElementTree
from src.node.schemas import NodeRead
from src.server.schemas import ServerRead
from src.payment.schemas import VDSRead


async def vds_install(server: ServerRead, server_node: NodeRead, server_vds: VDSRead, os: str) -> None:
    if os not in ("debian", "arch", "alpine", "gentoo", "freebsd", "openbsd"):
        raise ValueError("Invalid OS")

    with libvirt.open(f"qemu+ssh://{server_node.ip}/system") as conn:
        active_vds = conn.lookupByName(str(server.id))
        state, _ = active_vds.state()

        if state == libvirt.VIR_DOMAIN_RUNNING:
            active_vds.destroy()

        active_vds.undefine()

    subprocess.Popen(f"""ssh root@{server_node.ip} 'virt-install \
        --name {server.id} \
        --vcpus {server_vds.cores} \
        --memory {server_vds.ram * 1024} \
        --disk /var/lib/libvirt/images/{server.id}.qcow2,size={server_vds.disk_size} \
        --cdrom /opt/iso/{os}.iso \
        --os-variant unknown \
        --graphics vnc,listen={server_node.ip},port={server.vnc_port}'""", shell=True)


async def vds_delete(node_ip: str, name: str) -> None:
    with libvirt.open(f"qemu+ssh://{node_ip}/system") as conn:
        vds = conn.lookupByName(name)
        vds.destroy()
        vds.undefine()

    subprocess.run(f"ssh root@{node_ip} 'rm -f /var/lib/libvirt/images/{name}.qcow2'")


async def vds_action(server: ServerRead, server_node: NodeRead) -> None:
   with libvirt.open(f"qemu+ssh://{server_node.ip}/system") as conn:
       vds = conn.lookupByName(str(server.id))
       state, _ = vds.state()

       if state == libvirt.VIR_DOMAIN_SHUTOFF:
           vds.create()
       else:
           vds.destroy()


async def vds_status(server: ServerRead, server_node: NodeRead) -> dict:
    with libvirt.open(f"qemu+ssh://{server_node.ip}/system") as conn:
        vds = conn.lookupByName(str(server.id))
        interfaces = vds.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE)

        for _, iface_info in interfaces.items():
            for addr in iface_info["addrs"]:
                ipv4 = addr["addr"]

        state, _ = vds.state()

        if state == libvirt.VIR_DOMAIN_RUNNING:
            stat = "on"
        elif state == libvirt.VIR_DOMAIN_REBOOT_SIGNAL:
            stat = "reboot"
        elif state == libvirt.VIR_DOMAIN_SHUTOFF:
            stat = "off"
        else:
            stat = "uninstalled"

        return {"ipv4": ipv4, "status": stat}


async def vds_migrate(server: ServerRead, server_node: NodeRead, dst_node: NodeRead) -> None:
    with libvirt.open(f"qemu+ssh://{server_node.ip}/system") as conn:
        dom = conn.lookupByName(str(server.id))
        dom.migrateToURI(f"qemu+ssh://{dst_node.ip}/system", 0, None, 0)

        subprocess.run(f"scp root@{server_node.ip}:/var/lib/libvirt/images/{server.id}.qcow2 root@{dst_node.ip}:/var/lib/libvirt/images/{server.id}.qcow2")
        subprocess.run(f"ssh root@{server_node.ip} 'rm -f /var/lib/libvirt/images/{server.id}.qcow2'")


async def vds_upgrade(server: ServerRead, server_node: NodeRead, server_vds: VDSRead) -> None:
    with libvirt.open(f"qemu+ssh://{server_node.ip}/system") as conn:
        dom = conn.lookupByName(str(server.id))
        state, _ = dom.state()

        if state == libvirt.VIR_DOMAIN_RUNNING:
            dom.destroy()

        # Update cores and ram
        xml_desc = dom.XMLDesc()
        root = ElementTree.fromstring(xml_desc)

        vcpu_element = root.find("vcpu")

        if vcpu_element is not None:
            vcpu_element.text = f"{server_vds.cores}"

        memory_element = root.find("memory")

        if memory_element is not None:
            memory_element.text = f"{1024 * 1024 * server_vds.ram}"

        current_memory_element = root.find("currentMemory")

        if current_memory_element is not None:
            current_memory_element.text = f"{1024 * 1024 * server_vds.ram}"

        new_xml_desc = ElementTree.tostring(root, encoding="unicode")
        conn.createXML(new_xml_desc)

        # Update disk size
        subprocess.run(f"ssh root@{server_node.ip} 'qemu-img resize /var/lib/libvirt/images/{server.id}.qcow2 {server_vds.disk_size}G'")
