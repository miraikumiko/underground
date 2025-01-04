import asyncio
from datetime import datetime, timedelta
from underground.config import VDS_EXPIRED_DAYS
from underground.database import execute, fetchone, fetchall
from underground.server.utils import vds_delete


async def expired_check():
    servers = await fetchall("SELECT * FROM server")

    for server in servers:
        if datetime.strptime(server["end_at"], "%Y-%m-%d %H:%M:%S.%f") + timedelta(days=VDS_EXPIRED_DAYS) <= datetime.now():
            node = await fetchone("SELECT * FROM node WHERE id = ?", (server["node_id"],))
            await execute("DELETE FROM server WHERE id = ?", (server["id"],))
            await vds_delete(server["id"], node["ip"])


def expire():
    asyncio.run(expired_check())
