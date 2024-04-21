import requests
from requests.auth import HTTPDigestAuth
from src.config import RPC_SERVER_PORT, RPC_SERVER_USERNAME, RPC_SERVER_PASSWORD
from src.server.models import IPv4, IPv6


async def rpc_request(ip: str, method: str, params: dict = None) -> dict:
    if params is None:
        params = {}

    response = requests.post(f"http://{ip}:{RPC_SERVER_PORT}/json_rpc",
        json={
            "jsonrpc": "2.0",
            "id": "0",
            "method": method,
            "params": params
        }, headers={"Content-Type": "application/json"},
        auth=HTTPDigestAuth(RPC_SERVER_USERNAME, RPC_SERVER_PASSWORD)
    )

    return response.json()


async def rpc_get_av_specs(ip: str) -> dict:
    res = await rpc_request(ip, "get_av_specs")

    if res is not None:
        if res["status"] == "success":
            return res["specs"]
        else:
            raise Exception(res["detail"])


async def rpc_create_disk(ip: str, name: str, size: int):
    res = await rpc_request(ip, "create_disk", {"name": name, "size": size})

    if res is not None:
        if res["status"] == "error":
            raise Exception(res["detail"])


async def rpc_delete_disk(ip: str, name: str):
    res = await rpc_request(ip, "delete_disk", {"name": name, "size": size})

    if res is not None:
        if res["status"] == "error":
            raise Exception(res["detail"])
