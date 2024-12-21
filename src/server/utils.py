from datetime import datetime, timedelta, UTC
from starlette.exceptions import HTTPException
from src.database import Database, r
from src.config import VDS_DAYS, VDS_EXPIRED_DAYS
from src.logger import logger
from src.server.vds import vds_delete


async def request_vds(product_id: int, user: dict, is_active: bool = False) -> int:
    # Validate product id
    async with Database() as db:
        vds = await db.fetchone("SELECT * FROM vds WHERE id = ?", (product_id,))

    if not vds:
        raise HTTPException(400, "This product doesn't exist")

    async with Database() as db:
        servers = await db.fetchall("SELECT * FROM server")
        nodes = await db.fetchall(
            "SELECT * FROM node WHERE cores_available >= ? AND ram_available >= ? AND disk_size_available >= ?",
            (vds["cores"], vds["ram"], vds["disk_size"])
        )

    # Check availability of resources
    if not nodes:
        logger.warn(f"Haven't available resources for new vds {product_id} for {user['id']}")
        raise HTTPException(503, "We haven't available resources")

    node = nodes[0]

    # Reservation port for VNC
    vnc_port = 5900

    if servers:
        up = [server["vnc_port"] for server in servers if server["node_id"] == node["id"]]
        while vnc_port in up:
            vnc_port += 1

    # Registration of new server
    async with Database() as db:
        await db.execute(
            "UPDATE node SET cores_available = ?, ram_available = ?, disk_size_available = ? WHERE id = ?",
            (
                node["cores_available"] - vds["cores"],
                node["ram_available"] - vds["ram"],
                node["disk_size_available"] - vds["disk_size"],
                node["id"]
            )
        )
        await db.execute(
            "INSERT INTO server (vnc_port, start_at, end_at, is_active, in_upgrade, vds_id, node_id, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (vnc_port, datetime.now(UTC), datetime.now() + timedelta(days=VDS_DAYS), is_active, 0, product_id, node["id"], user["id"])
        )
        server_id = await db.fetchone("SELECT last_insert_rowid()")
        server_id = server_id[0]

    return server_id


async def servers_expired_check():
    async with Database() as db:
        servers = await db.fetchall("SELECT * FROM server")

    for server in servers:
        # Delete expired server
        if server["end_at"] + timedelta(days=VDS_EXPIRED_DAYS) <= datetime.now():
            async with Database() as db:
                node = await db.fetchone("SELECT * FROM node WHERE id = ?", (server["node_id"],))
                await db.execute("DELETE FROM server WHERE id = ?", (server["id"],))

            await vds_delete(server["id"], node["ip"])

            logger.info(f"Server {server['id']} has been expired and deleted")
        elif server["end_at"] <= datetime.now():
            logger.info(f"Server {server['id']} has been expired")

        # Free node specs from unpaid upgrade
        if server["in_upgrade"]:
            is_upgraded = await r.get(f"upgrade_server:{server['id']}")

            if not is_upgraded:
                # Update node specs
                async with Database() as db:
                    node = await db.fetchone("SELECT * FROM node WHERE id = ?", (server["node_id"],))
                    server_vds = await db.fetchone("SELECT * FROM vds WHERE id = ?", (server["vds_id"],))
                    dst_node_id = await r.get(f"node_to_migrate:{server['id']}")
                    upgrade_vds_id = await r.get(f"unupgraded_server:{server['id']}")
                    upgrade_vds = await db.fetchone("SELECT * FROM vds WHERE id = ?", (upgrade_vds_id,))

                if dst_node_id:
                    async with Database() as db:
                        dst_node = await db.fetchone("SELECT * FROM node WHERE id = ?", (dst_node_id,))
                        await db.execute(
                            "UPDATE node SET cores_available = ?, ram_available = ?, disk_size_available = ? WHERE id = ?",
                            (
                                dst_node["cores_available"] + upgrade_vds["cores"] - server_vds["cores"],
                                dst_node["ram_available"] + upgrade_vds["ram"] - server_vds["ram"],
                                dst_node["disk_size_available"] + upgrade_vds["disk_size"] - server_vds["disk_size"],
                                dst_node["id"]
                            )
                        )
                else:
                    async with Database() as db:
                        await db.execute(
                            "UPDATE node SET cores_available = ?, ram_available = ?, disk_size_available = ? WHERE id = ?",
                            (
                                node["cores_available"] + upgrade_vds["cores"] - server_vds["cores"],
                                node["ram_available"] + upgrade_vds["ram"] - server_vds["ram"],
                                node["disk_size_available"] + upgrade_vds["disk_size"] - server_vds["disk_size"],
                                server["node_id"]
                            )
                        )

                # Update server
                async with Database() as db:
                    await db.execute("UPDATE server SET in_upgrade = ? WHERE id = ?", (0, server["id"]))

                # Delete markers
                await r.delete(f"node_to_migrate:{server['id']}")
                await r.delete(f"unupgraded_server:{server['id']}")

        # Delete unpaid server
        if not server.is_active:
            is_not_expired = await r.get(f"inactive_server:{server['id']}")

            if not is_not_expired:
                # Update node specs
                async with Database() as db:
                    node = await db.fetchone("SELECT * FROM node WHERE id = ?", (server["node_id"],))
                    vds = await db.fetchone("SELECT * FROM vds WHERE id = ?", (server["vds_id"],))

                    cores = node["cores_available"] + vds["cores"]
                    ram = node["ram_available"] + vds["ram"]
                    disk_size = node["disk_size_available"] + vds["disk_size"]

                    if vds["cores"] > node["cores"]:
                        cores = node["cores"]

                    if vds["ram"] > node["ram"]:
                        ram = node["ram"]

                    if vds["disk_size"] > node["disk_size"]:
                        disk_size = node["disk_size"]

                    await db.execute(
                        "UPDATE node SET cores_available = ?, ram_available = ?, disk_size_available = ? WHERE id = ?",
                        (cores, ram, disk_size, server["node_id"])
                    )

                    # Delete server
                    await db.execute("DELETE FROM server WHERE id = ?", (server["id"],))

                logger.info(f"Server {server['id']} has been deleted")
