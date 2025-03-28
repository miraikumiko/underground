from pathlib import Path
from starlette.config import Config
from databases import DatabaseURL
import underground

BASE_DIR = Path(underground.__file__).parent.resolve()

config = Config("/etc/underground.conf")

TESTING = config("TESTING", cast=bool, default=False)
REGISTRATION = config("REGISTRATION", cast=bool, default=True)

HOST = config("HOST", default="127.0.0.1")
PORT = config("PORT", cast=int, default=8000)

DATABASE_URL = config("DATABASE_URL", cast=DatabaseURL, default=DatabaseURL("postgresql://underground:underground@localhost/underground"))
DATABASE_TEST_URL = DATABASE_URL.replace(database="test_" + DATABASE_URL.database)

IMAGES_PATH = config("IMAGES_PATH", default="/var/lib/libvirt/images")

VDS_DAYS = config("VDS_DAYS", cast=int, default=31)
VDS_MAX_PAYED_DAYS = config("VDS_MAX_PAYED_DAYS", cast=int, default=90)
VDS_EXPIRED_DAYS = config("VDS_EXPIRED_DAYS", cast=int, default=3)

MONERO_RPC_IP = config("MONERO_RPC_IP", default="127.0.0.1")
MONERO_RPC_PORT = config("MONERO_RPC_PORT", cast=int, default=20000)
MONERO_RPC_USERNAME = config("MONERO_RPC_USERNAME", default="underground")
MONERO_RPC_PASSWORD = config("MONERO_RPC_PASSWORD", default="underground")
