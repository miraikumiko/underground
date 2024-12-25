from datetime import datetime, timedelta, UTC
from starlette.exceptions import HTTPException
from src.database import r, execute, fetchone, fetchall
from src.config import VDS_DAYS, VDS_EXPIRED_DAYS
from src.server.vds import vds_delete


async def request_vds(product_id: int, user: dict, is_active: bool = False) -> int:
    # Validate product id
    vds = await fetchone("SELECT * FROM vds WHERE id = ?", (product_id,))

    if not vds:
        raise HTTPException(400, "This product doesn't exist")

    servers = await fetchall("SELECT * FROM server")
    nodes = await fetchall(
        "SELECT * FROM node WHERE cores_available >= ? AND ram_available >= ? AND disk_size_available >= ?",
        (vds["cores"], vds["ram"], vds["disk_size"])
    )

    # Check availability of resources
    if not nodes:
        raise HTTPException(503, "We haven't available resources")

    node = nodes[0]

    # Reservation port for VNC
    vnc_port = 5900

    if servers:
        up = [server["vnc_port"] for server in servers if server["node_id"] == node["id"]]
        while vnc_port in up:
            vnc_port += 1

    # Registration of new server
    await execute(
        "UPDATE node SET cores_available = ?, ram_available = ?, disk_size_available = ? WHERE id = ?",
        (
            node["cores_available"] - vds["cores"],
            node["ram_available"] - vds["ram"],
            node["disk_size_available"] - vds["disk_size"],
            node["id"]
        )
    )

    server_id = await execute(
        "INSERT INTO server (vnc_port, start_at, end_at, is_active, in_upgrade, vds_id, node_id, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (vnc_port, datetime.now(UTC), datetime.now() + timedelta(days=VDS_DAYS), is_active, 0, product_id, node["id"], user["id"])
    )

    return server_id


async def servers_expired_check():
    servers = await fetchall("SELECT * FROM server")

    for server in servers:
        # Delete expired server
        if datetime.strptime(server["end_at"], "%Y-%m-%d %H:%M:%S.%f") + timedelta(days=VDS_EXPIRED_DAYS) <= datetime.now():
            node = await fetchone("SELECT * FROM node WHERE id = ?", (server["node_id"],))
            await execute("DELETE FROM server WHERE id = ?", (server["id"],))
            await vds_delete(server["id"], node["ip"])

        # Free node specs from unpaid upgrade
        if server["in_upgrade"]:
            is_upgraded = await r.get(f"upgrade_server:{server['id']}")

            if not is_upgraded:
                # Update node specs
                node = await fetchone("SELECT * FROM node WHERE id = ?", (server["node_id"],))
                server_vds = await fetchone("SELECT * FROM vds WHERE id = ?", (server["vds_id"],))
                dst_node_id = await r.get(f"node_to_migrate:{server['id']}")
                upgrade_vds_id = await r.get(f"unupgraded_server:{server['id']}")
                upgrade_vds = await fetchone("SELECT * FROM vds WHERE id = ?", (upgrade_vds_id,))

                if dst_node_id:
                    dst_node = await fetchone("SELECT * FROM node WHERE id = ?", (dst_node_id,))
                    await execute(
                        "UPDATE node SET cores_available = ?, ram_available = ?, disk_size_available = ? WHERE id = ?",
                        (
                            dst_node["cores_available"] + upgrade_vds["cores"] - server_vds["cores"],
                            dst_node["ram_available"] + upgrade_vds["ram"] - server_vds["ram"],
                            dst_node["disk_size_available"] + upgrade_vds["disk_size"] - server_vds["disk_size"],
                            dst_node["id"]
                        )
                    )
                else:
                    await execute(
                        "UPDATE node SET cores_available = ?, ram_available = ?, disk_size_available = ? WHERE id = ?",
                        (
                            node["cores_available"] + upgrade_vds["cores"] - server_vds["cores"],
                            node["ram_available"] + upgrade_vds["ram"] - server_vds["ram"],
                            node["disk_size_available"] + upgrade_vds["disk_size"] - server_vds["disk_size"],
                            server["node_id"]
                        )
                    )

                # Update server
                await execute("UPDATE server SET in_upgrade = ? WHERE id = ?", (0, server["id"]))

                # Delete markers
                await r.delete(f"node_to_migrate:{server['id']}")
                await r.delete(f"unupgraded_server:{server['id']}")

        # Delete unpaid server
        if not server["is_active"]:
            is_not_expired = await r.get(f"inactive_server:{server['id']}")

            if not is_not_expired:
                # Update node specs
                node = await fetchone("SELECT * FROM node WHERE id = ?", (server["node_id"],))
                vds = await fetchone("SELECT * FROM vds WHERE id = ?", (server["vds_id"],))

                cores = node["cores_available"] + vds["cores"]
                ram = node["ram_available"] + vds["ram"]
                disk_size = node["disk_size_available"] + vds["disk_size"]

                if vds["cores"] > node["cores"]:
                    cores = node["cores"]

                if vds["ram"] > node["ram"]:
                    ram = node["ram"]

                if vds["disk_size"] > node["disk_size"]:
                    disk_size = node["disk_size"]

                await execute(
                    "UPDATE node SET cores_available = ?, ram_available = ?, disk_size_available = ? WHERE id = ?",
                    (cores, ram, disk_size, server["node_id"])
                )

                # Delete server
                await execute("DELETE FROM server WHERE id = ?", (server["id"],))
