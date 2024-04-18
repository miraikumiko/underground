import requests
from src.config import RPC_SERVER_PORT, RPC_SERVER_KEY


async def rpc_create_disk(ip: str, name: str, size: int) -> int:
    response = requests.get(f"https://{ip}:{RPC_SERVER_PORT}", {
        "key": RPC_SERVER_KEY,
        "operation": "create_disk",
        "params": {"name": name, "size": size}
    }).json()

    return 1 if response["status"] == "success" else 0


async def rpc_get_available_cores_number(ip: str) -> int:
    response = requests.get(f"https://{ip}:{RPC_SERVER_PORT}", {
        "key": RPC_SERVER_KEY,
        "operation": "get_cores"
    }).json()

    if response is not None:
        cores_count = response["cores_count"]

        return cores_count


async def rpc_get_ipv4(ip: str) -> str:
    import random
    return f"111.111.111.{random.randint(1, 255)}"
    #response = requests.get(f"https://{ip}:{RPC_SERVER_PORT}", {
    #    "key": RPC_SERVER_KEY,
    #    "operation": "get_ipv4"
    #}).json()

    #if response is not None:
    #    ipv4 = response["ipv4"]

    #    return ipv4


async def rpc_get_ipv6(ip: str) -> str:
    response = requests.get(f"https://{ip}:{RPC_SERVER_PORT}", {
        "key": RPC_SERVER_KEY,
        "operation": "get_ipv6"
    }).json()

    if response is not None:
        ipv6 = response["ipv6"]

        return ipv6


async def rpc_delete_vps(server_id: int, ip: str) -> int:
    response = requests.get(f"https://{ip}:{RPC_SERVER_PORT}", {
        "key": RPC_SERVER_KEY,
        "operation": "delete_vps",
        "params": {"name": str(server_id)}
    }).json()

    return 1 if response["status"] == "success" else 0
