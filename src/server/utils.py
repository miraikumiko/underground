from datetime import datetime, timedelta, UTC
from starlette.exceptions import HTTPException
from src.database import Database, r
from src.config import VDS_DAYS, VDS_EXPIRED_DAYS
from src.logger import logger
from src.server.vds import vds_delete


async def request_vds(product_id: int, user: tuple, is_active: bool = False) -> int:
    # Validate product id
    async with Database() as db:
        vds = await db.fetchone("SELECT * FROM vds WHERE id = ?", (product_id,))

    if not vds:
        raise HTTPException(400, "This product doesn't exist")

    async with Database() as db:
        servers = await db.fetchall("SELECT * FROM server")
        nodes = await db.fetchall(
            "SELECT * FROM node WHERE cores_available >= ? AND ram_available >= ? AND disk_size_available >= ?",
            (vds[1], vds[2], vds[3])
        )

    # Check availability of resources
    if not nodes:
        logger.warn(f"Haven't available resources for new vds {product_id} for {user[0]}")
        raise HTTPException(503, "We haven't available resources")

    node = nodes[0]

    # Reservation port for VNC
    vnc_port = 5900

    if servers:
        up = [server[1] for server in servers if server[7] == node[0]]
        while vnc_port in up:
            vnc_port += 1

    # Registration of new server
    async with Database() as db:
        await db.execute(
            "UPDATE node SET cores_available = ?, ram_available = ?, disk_size_available = ? WHERE id = ?",
            (node[3] - vds[1], node[5] - vds[2], node[7] - vds[3], node[0])
        )
        await db.execute(
            "INSERT INTO server (vnc_port, start_at, end_at, is_active, in_upgrade, vds_id, node_id, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (vnc_port, datetime.now(UTC), datetime.now() + timedelta(days=VDS_DAYS), is_active, 0, product_id, node[0], user[0])
        )
        server_id = await db.fetchone("SELECT last_insert_rowid()")
        server_id = server_id[0]

    return server_id


async def servers_expired_check():
    async with Database() as db:
        servers = await db.fetchall("SELECT * FROM server")

    for server in servers:
        # Delete expired server
        if server[3] + timedelta(days=VDS_EXPIRED_DAYS) <= datetime.now():
            async with Database() as db:
                node = await db.fetchone("SELECT * FROM node WHERE id = ?", (server[7],))
                await db.execute("DELETE FROM server WHERE id = ?", (server[0],))

            await vds_delete(server[0], node[1])

            logger.info(f"Server {server[0]} has been expired and deleted")
        elif server[3] <= datetime.now():
            logger.info(f"Server {server[0]} has been expired")

        # Free node specs from unpaid upgrade
        if server[5]:
            is_upgraded = await r.get(f"upgrade_server:{server[0]}")

            if not is_upgraded:
                # Update node specs
                async with Database() as db:
                    node = await db.fetchone("SELECT * FROM node WHERE id = ?", (server[7],))
                    server_vds = await db.fetchone("SELECT * FROM vds WHERE id = ?", (server[6],))
                    dst_node_id = await r.get(f"node_to_migrate:{server[0]}")
                    upgrade_vds_id = await r.get(f"unupgraded_server:{server[0]}")
                    upgrade_vds = await db.fetchone("SELECT * FROM vds WHERE id = ?", (upgrade_vds_id,))

                if dst_node_id:
                    async with Database() as db:
                        dst_node = await db.fetchone("SELECT * FROM node WHERE id = ?", (dst_node_id,))
                        await db.execute(
                            "UPDATE node SET cores_available = ?, ram_available = ?, disk_size_available = ? WHERE id = ?",
                            (
                                dst_node[3] + upgrade_vds[1] - server_vds[1],
                                dst_node[5] + upgrade_vds[2] - server_vds[2],
                                dst_node[7] + upgrade_vds[3] - server_vds[3],
                                dst_node[0]
                            )
                        )
                else:
                    async with Database() as db:
                        await db.execute(
                            "UPDATE node SET cores_available = ?, ram_available = ?, disk_size_available = ? WHERE id = ?",
                            (
                                node[3] + upgrade_vds[1] - server_vds[1],
                                node[5] + upgrade_vds[2] - server_vds[2],
                                node[7] + upgrade_vds[3] - server_vds[3],
                                server[7]
                            )
                        )

                # Update server
                async with Database() as db:
                    await db.execute("UPDATE server SET in_upgrade = ? WHERE id = ?", (0, server[0]))

                # Delete markers
                await r.delete(f"node_to_migrate:{server[0]}")
                await r.delete(f"unupgraded_server:{server[0]}")

        # Delete unpaid server
        if not server.is_active:
            is_not_expired = await r.get(f"inactive_server:{server[0]}")

            if not is_not_expired:
                # Update node specs
                async with Database() as db:
                    node = await db.fetchone("SELECT * FROM node WHERE id = ?", (server[7],))
                    vds = await db.fetchone("SELECT * FROM vds WHERE id = ?", (server[6],))

                    cores = node[3] + vds[1]
                    ram = node[5] + vds[2]
                    disk_size = node[7] + vds[3]

                    if vds[1] > node[2]:
                        cores = node[2]

                    if vds[2] > node[4]:
                        ram = node[4]

                    if vds[3] > node[6]:
                        disk_size = node[6]

                    await db.execute(
                        "UPDATE node SET cores_available = ?, ram_available = ?, disk_size_available = ? WHERE id = ?",
                        (cores, ram, disk_size, server[7])
                    )

                    # Delete server
                    await db.execute("DELETE FROM server WHERE id = ?", (server[0],))

                logger.info(f"Server {server[0]} has been deleted")
