import requests
from src.config import RPC_SERVER_PORT, RPC_SERVER_KEY


async def rpc_create_disk(ip: str, name: str, size: int) -> int:
    try:
        response = requests.get(f"https://{ip}:{RPC_SERVER_PORT}", {
            "key": RPC_SERVER_KEY,
            "operation": "create_disk",
            "params": {"name": name, "size": size}
        })

        return 1 if response.json()["status"] == "success" else 0
    except Exception as e:
        raise e


async def rpc_get_avaible_cores_number(ip: str) -> int:
    try:
        response = requests.get(f"https://{ip}:{RPC_SERVER_PORT}", {
            "key": RPC_SERVER_KEY,
            "operation": "get_cores"
        })

        return response
    except Exception as e:
        raise e


async def rpc_get_ipv4(ip: str) -> str:
    try:
        response = requests.get(f"https://{ip}:{RPC_SERVER_PORT}", {
            "key": RPC_SERVER_KEY,
            "operation": "get_ipv4"
        })

        return response
    except Exception as e:
        raise e


async def rpc_get_ipv6(ip: str) -> str:
    try:
        response = requests.get(f"https://{ip}:{RPC_SERVER_PORT}", {
            "key": RPC_SERVER_KEY,
            "operation": "get_ipv6"
        })

        return response
    except Exception as e:
        raise e
