import asyncio
from datetime import datetime, timedelta
from underground.config import VDS_EXPIRED_DAYS
from underground.database import database
from underground.models import *
from underground.utils.server import vds_delete


async def expired_check():
    servers = await database.fetch_all(Server.select())

    for server in servers:
        if datetime.fromisoformat(server.end_at + timedelta(days=VDS_EXPIRED_DAYS) <= datetime.now()):
            node = await database.fetch_one(Node.select().where(Node.c.id == server.node_id))
            await database.execute(Server.delete().where(server.c.id == server.id))
            await vds_delete(server.id, node.ip)


def expire():
    asyncio.run(expired_check())
