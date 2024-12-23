import subprocess
import libvirt
from xml.etree import ElementTree
from src.config import IMAGES_PATH


async def vds_install(server: dict, server_node_ip: str, server_vds: dict, os: dict) -> None:
    with libvirt.open(f"qemu+ssh://{server_node_ip}/system") as conn:
        dom = conn.lookupByName(str(server["id"]))
        state, _ = dom.state()

        if state == libvirt.VIR_DOMAIN_RUNNING:
            dom.destroy()

        dom.undefine()

    subprocess.Popen(f"""ssh root@{server_node_ip} 'virt-install \
        --name {server['id']} \
        --vcpus {server_vds['cores']} \
        --memory {server_vds['ram'] * 1024} \
        --disk {IMAGES_PATH}/{server['id']}.qcow2,size={server_vds['disk_size']} \
        --os-variant {os['name']} \
        --cdrom /srv/iso/{os['file']} \
        --graphics vnc,listen={server_node_ip},port={server['vnc_port']}'""", shell=True)


async def vds_delete(server_id: int, server_node_ip: str) -> None:
    with libvirt.open(f"qemu+ssh://{server_node_ip}/system") as conn:
        dom = conn.lookupByName(str(server_id))
        dom.destroy()
        dom.undefine()

    subprocess.run(f"ssh root@{server_node_ip} 'rm -f {IMAGES_PATH}/{server_id}.qcow2'")


async def vds_action(server_id: int, server_node_ip: str) -> None:
   with libvirt.open(f"qemu+ssh://{server_node_ip}/system") as conn:
       dom = conn.lookupByName(str(server_id))
       state, _ = dom.state()

       if state == libvirt.VIR_DOMAIN_SHUTOFF:
           dom.create()
       else:
           dom.destroy()


async def vds_status(server_id: int, server_node_ip: str) -> dict:
    with libvirt.open(f"qemu+ssh://{server_node_ip}/system") as conn:
        status = {"ipv4": None, "ipv6": None, "status": None}

        try:
            dom = conn.lookupByName(str(server_id))
            interfaces = dom.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE)

            for _, iface_info in interfaces.items():
                addrs = iface_info.get("addrs", [])

                if addrs:
                    for i in range(2):
                        if len(addrs) > i:
                            prefix = addrs[i].get("prefix")

                            if prefix <= 32:
                                status["ipv4"] = addrs[i].get("addr")
                            else:
                                status["ipv6"] = addrs[i].get("addr")

            state, _ = dom.state()

            if state == libvirt.VIR_DOMAIN_RUNNING:
                status["status"] = "on"
            else:
                status["status"] = "off"
        except libvirt.libvirtError:
            pass

        return status


async def vds_migrate(server_id: int, server_node_ip: str, dst_node_ip: str) -> None:
    with libvirt.open(f"qemu+ssh://{server_node_ip}/system") as conn:
        dom = conn.lookupByName(str(server_id))
        dom.migrateToURI(f"qemu+ssh://{dst_node_ip}/system", 0, None, 0)

        subprocess.run(f"scp root@{server_node_ip}:{IMAGES_PATH}/{server_id}.qcow2 root@{dst_node_ip}:{IMAGES_PATH}/{server_id}.qcow2")
        subprocess.run(f"ssh root@{server_node_ip} 'rm -f {IMAGES_PATH}/{server_id}.qcow2'")


async def vds_upgrade(server_id: int, server_node_ip: str, server_vds: dict) -> None:
    with libvirt.open(f"qemu+ssh://{server_node_ip}/system") as conn:
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

        # Resize the disk
        subprocess.run(f"ssh root@{server_node_ip} 'qemu-img resize {IMAGES_PATH}/{server_id}.qcow2 {server_vds['disk_size']}G'")
