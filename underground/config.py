from pathlib import Path
from starlette.config import Config
import databases
import underground

BASE_DIR = Path(underground.__file__).parent.resolve()

config = Config("/etc/environment")

TESTING = config("TESTING", cast=bool, default=False)
REGISTRATION = config("REGISTRATION", cast=bool, default=True)

HOST = config("HOST")
PORT = config("PORT", cast=int)

DATABASE_URL = config("DATABASE_URL", cast=databases.DatabaseURL)
TEST_DATABASE_URL = DATABASE_URL.replace(database="test_" + DATABASE_URL.database)

IMAGES_PATH = config("IMAGES_PATH")

VDS_DAYS = config("VDS_DAYS", cast=int)
VDS_MAX_PAYED_DAYS = config("VDS_MAX_PAYED_DAYS", cast=int)
VDS_EXPIRED_DAYS = config("VDS_EXPIRED_DAYS", cast=int)

MONERO_RPC_IP = config("MONERO_RPC_IP")
MONERO_RPC_PORT = config("MONERO_RPC_PORT", cast=int)
MONERO_RPC_USERNAME = config("MONERO_RPC_USERNAME")
MONERO_RPC_PASSWORD = config("MONERO_RPC_PASSWORD")
