import subprocess
from xml.etree import ElementTree
import libvirt
from src.config import IMAGES_PATH

libvirt.registerErrorHandler(lambda _, __: None, None)


async def vds_install(server: dict, server_node_ip: str, server_vds: dict, os: str) -> None:
    with libvirt.open(f"qemu+ssh://{server_node_ip}/system") as conn:
        try:
            dom = conn.lookupByName(str(server["id"]))
            state, _ = dom.state()

            if state == libvirt.VIR_DOMAIN_RUNNING:
                dom.destroy()

            dom.undefine()
        except libvirt.libvirtError:
            pass

        try:
            subprocess.run(f"""ssh root@{server_node_ip} 'virt-install \
                --name {server['id']} \
                --vcpus {server_vds['cores']} \
                --memory {server_vds['ram'] * 1024} \
                --disk {IMAGES_PATH}/{server['id']}.qcow2,size={server_vds['disk_size']} \
                --network default \
                --os-variant {os} \
                --cdrom /opt/iso/{os}.iso \
                --graphics vnc,listen={server_node_ip},port={server['vnc_port']}'""", shell=True, check=True)
        except subprocess.CalledProcessError:
            pass


async def vds_delete(server_id: int, server_node_ip: str) -> None:
    with libvirt.open(f"qemu+ssh://{server_node_ip}/system") as conn:
        try:
            dom = conn.lookupByName(str(server_id))
            dom.destroy()
            dom.undefine()
        except libvirt.libvirtError:
            pass

        try:
            subprocess.run(f"ssh root@{server_node_ip} 'rm -f {IMAGES_PATH}/{server_id}.qcow2'", shell=True, check=True)
        except subprocess.CalledProcessError:
            pass


async def vds_action(server_id: int, server_node_ip: str) -> None:
    with libvirt.open(f"qemu+ssh://{server_node_ip}/system") as conn:
        try:
            dom = conn.lookupByName(str(server_id))
            state, _ = dom.state()

            if state == libvirt.VIR_DOMAIN_SHUTOFF:
                dom.create()
            else:
                dom.destroy()
        except libvirt.libvirtError:
            pass


async def vds_status(server_id: int, server_node_ip: str) -> dict:
    status = {"ipv4": None, "ipv6": None, "status": None}

    with libvirt.open(f"qemu+ssh://{server_node_ip}/system") as conn:
        try:
            dom = conn.lookupByName(str(server_id))
            interfaces = dom.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE)

            for iface_info in interfaces.values():
                for addr in iface_info.get("addrs", [])[:2]:
                    prefix = addr.get("prefix")

                    if prefix <= 32:
                        status["ipv4"] = addr.get("addr")
                        break

                    if prefix > 32:
                        status["ipv6"] = addr.get("addr")
                        break

            state, _ = dom.state()

            if state == libvirt.VIR_DOMAIN_RUNNING:
                status["status"] = "on"

        except libvirt.libvirtError:
            pass

        return status


async def vds_migrate(server_id: int, server_node_ip: str, dst_node_ip: str) -> None:
    with libvirt.open(f"qemu+ssh://{server_node_ip}/system") as conn:
        try:
            dom = conn.lookupByName(str(server_id))
            dom.migrateToURI(f"qemu+ssh://{dst_node_ip}/system")
        except libvirt.libvirtError:
            pass

        try:
            subprocess.run(f"scp root@{server_node_ip}:{IMAGES_PATH}/{server_id}.qcow2 root@{dst_node_ip}:{IMAGES_PATH}/{server_id}.qcow2", shell=True, check=True)
            subprocess.run(f"ssh root@{server_node_ip} 'rm -f {IMAGES_PATH}/{server_id}.qcow2'", shell=True, check=True)
        except subprocess.CalledProcessError:
            pass


async def vds_upgrade(server_id: int, server_node_ip: str, server_vds: dict) -> None:
    with libvirt.open(f"qemu+ssh://{server_node_ip}/system") as conn:
        try:
            dom = conn.lookupByName(str(server_id))
            state, _ = dom.state()

            if state == libvirt.VIR_DOMAIN_RUNNING:
                dom.destroy()

            # Update count of cores and ram
            xml_desc = dom.XMLDesc()
            root = ElementTree.fromstring(xml_desc)

            vcpu_element = root.find("vcpu")

            if vcpu_element is not None:
                vcpu_element.text = f"{server_vds['cores']}"

            memory_element = root.find("memory")

            if memory_element is not None:
                memory_element.text = f"{1024 * 1024 * server_vds['ram']}"

            current_memory_element = root.find("currentMemory")

            if current_memory_element is not None:
                current_memory_element.text = f"{1024 * 1024 * server_vds['ram']}"

            new_xml_desc = ElementTree.tostring(root, encoding="unicode")
            conn.createXML(new_xml_desc)
        except libvirt.libvirtError:
            pass

        # Resize the disk
        try:
            subprocess.run(f"ssh root@{server_node_ip} 'qemu-img resize {IMAGES_PATH}/{server_id}.qcow2 {server_vds['disk_size']}G'", shell=True, check=True)
        except subprocess.CalledProcessError:
            pass
