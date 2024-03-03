import requests
from src.utils import err_catch
from src.config import RPC_SERVER_PORT, RPC_SERVER_KEY


@err_catch
async def rpc_create_disk(ip: str, name: str, size: int) -> int:
    response = requests.get(f"https://{ip}:{RPC_SERVER_PORT}", {
        "key": RPC_SERVER_KEY,
        "operation": "create_disk",
        "params": {"name": name, "size": size}
    })

    return 1 if response.json()["status"] == "success" else 0


@err_catch
async def rpc_get_available_cores_number(ip: str) -> int:
    response = requests.get(f"https://{ip}:{RPC_SERVER_PORT}", {
        "key": RPC_SERVER_KEY,
        "operation": "get_cores"
    }).json()

    if response is not None:
        cores_count = response["cores_count"]

        return cores_count


@err_catch
async def rpc_get_ipv4(ip: str) -> str:
    response = requests.get(f"https://{ip}:{RPC_SERVER_PORT}", {
        "key": RPC_SERVER_KEY,
        "operation": "get_ipv4"
    }).json()

    if response is not None:
        ipv4 = response["ipv4"]

        return ipv4


@err_catch
async def rpc_get_ipv6(ip: str) -> str:
    response = requests.get(f"https://{ip}:{RPC_SERVER_PORT}", {
        "key": RPC_SERVER_KEY,
        "operation": "get_ipv6"
    }).json()

    if response is not None:
        ipv6 = response["ipv6"]

        return ipv6
