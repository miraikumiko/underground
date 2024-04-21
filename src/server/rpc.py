import requests
from requests.auth import HTTPDigestAuth
from src.logger import logger
from src.config import RPC_SERVER_PORT, RPC_SERVER_USERNAME, RPC_SERVER_PASSWORD
from src.server.models import IPv4, IPv6


async def rpc_request(ip: str, method: str, params: dict = None) -> dict:
    if params is None:
        params = {}

    res = requests.post(f"http://{ip}:{RPC_SERVER_PORT}/json_rpc",
        json={
            "jsonrpc": "2.0",
            "id": "0",
            "method": method,
            "params": params
        }, headers={"Content-Type": "application/json"},
        auth=HTTPDigestAuth(RPC_SERVER_USERNAME, RPC_SERVER_PASSWORD)
    )
    
    if res.status_code == 500:
        raise Exception("Server error")

    return res.json()


async def rpc_get_av_specs(ip: str) -> dict:
    try:
        specs = await rpc_request(ip, "get_av_specs")

        return specs
    except Exception as e:
        logger.error(e)
        raise e


async def rpc_create_disk(ip: str, name: str, size: int):
    try:
        await rpc_request(ip, "create_disk", {"name": name, "size": size})
    except Exception as e:
        logger.error(e)
        raise e


async def rpc_delete_disk(ip: str, name: str):
    try:
        await rpc_request(ip, "delete_disk", {"name": name, "size": size})
    except Exception as e:
        logger.error(e)
        raise e
