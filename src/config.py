from os import environ, path
from dotenv import load_dotenv

load_dotenv()

# App
HOST = environ.get("HOST")
PORT = environ.get("PORT")
LOG_FILE = environ.get("LOG_FILE")
REGISTRATION = environ.get("REGISTRATION")
PAYMENT_TIME = environ.get("PAYMENT_TIME")
PAYMENT_LIMIT = environ.get("PAYMENT_LIMIT")
VDS_DAYS = environ.get("VDS_DAYS")
VDS_MAX_PAYED_DAYS = environ.get("VDS_MAX_PAYED_DAYS")
VDS_EXPIRED_DAYS = environ.get("VDS_EXPIRED_DAYS")
IMAGES_PATH = environ.get("IMAGES_PATH")

# Database
DB_PATH = environ.get("DB_PATH")

# Redis
REDIS_HOST = environ.get("REDIS_HOST")
REDIS_PORT = environ.get("REDIS_PORT")

# Monero
MONERO_RPC_IP = environ.get("MONERO_RPC_IP")
MONERO_RPC_PORT = environ.get("MONERO_RPC_PORT")
MONERO_RPC_USER = environ.get("MONERO_RPC_USER")
MONERO_RPC_PASSWORD = environ.get("MONERO_RPC_PASSWORD")

# Subnet
SUBNET_IPV4 = environ.get("SUBNET_IPV4")
SUBNET_IPV6 = environ.get("SUBNET_IPV6")

# Type correction
PORT = int(PORT)
REGISTRATION = True if REGISTRATION == "true" else False
PAYMENT_TIME = int(PAYMENT_TIME)
PAYMENT_LIMIT = int(PAYMENT_LIMIT)
VDS_DAYS = int(VDS_DAYS)
VDS_MAX_PAYED_DAYS = int(VDS_MAX_PAYED_DAYS)
VDS_EXPIRED_DAYS = int(VDS_EXPIRED_DAYS)
REDIS_PORT = int(REDIS_PORT)
MONERO_RPC_PORT = int(MONERO_RPC_PORT)

# Base path of project
BASE_PATH = path.dirname(path.dirname(path.realpath(__file__)))
