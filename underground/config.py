from pathlib import Path
from starlette.config import Config
import underground

BASE_DIR = Path(underground.__file__).parent.resolve()

config = Config("/etc/environment")

HOST = config("HOST")
PORT = config("PORT", cast=int)

DB_URL = config("DB_URL")
IMAGES_PATH = config("IMAGES_PATH")

REGISTRATION = config("REGISTRATION", cast=bool)

VDS_DAYS = config("VDS_DAYS", cast=int)
VDS_MAX_PAYED_DAYS = config("VDS_MAX_PAYED_DAYS", cast=int)
VDS_EXPIRED_DAYS = config("VDS_EXPIRED_DAYS", cast=int)

MONERO_RPC_IP = config("MONERO_RPC_IP")
MONERO_RPC_PORT = config("MONERO_RPC_PORT", cast=int)
MONERO_RPC_USERNAME = config("MONERO_RPC_USERNAME")
MONERO_RPC_PASSWORD = config("MONERO_RPC_PASSWORD")
