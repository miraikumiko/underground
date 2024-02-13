from requests import get
from src.config import RPC_KEY


async def rpc_create_disk(ip: str, name: str, size: int) -> int | Exception:
    try:
        response = get(f"https://{ip}:55055", {
            "key": RPC_KEY,
            "operation": "create_disk",
            "params": {"name": name, "size": size}
        })

        return 1 if response else 0
    except Exception as e:
        raise e


async def rpc_get_avaible_cores_number(ip: str) -> int | Exception:
    try:
        response = get(f"https://{ip}:55055", {"key": RPC_KEY, "operation": "get_cores"})

        return response
    except Exception as e:
        raise e


async def rpc_get_ipv4(ip: str) -> str | Exception:
    try:
        response = get(f"https://{ip}:55055", {"key": RPC_KEY, "operation": "get_ipv4"})

        return response
    except Exception as e:
        raise e


async def rpc_get_ipv6(ip: str) -> str | Exception:
    try:
        response = get(f"https://{ip}:55055", {"key": RPC_KEY, "operation": "get_ipv6"})

        return response
    except Exception as e:
        raise e
