from os import environ, path
from dotenv import load_dotenv

load_dotenv()

BASE_PATH = path.dirname(path.dirname(path.realpath(__file__)))

HOST = environ.get("HOST")
PORT = int(environ.get("PORT"))

DB_PATH = environ.get("DB_PATH")
LOG_PATH = environ.get("LOG_PATH")
IMAGES_PATH = environ.get("IMAGES_PATH")

REGISTRATION = int(environ.get("REGISTRATION"))

PAYMENT_TIME = int(environ.get("PAYMENT_TIME"))
PAYMENT_LIMIT = int(environ.get("PAYMENT_LIMIT"))

VDS_DAYS = int(environ.get("VDS_DAYS"))
VDS_MAX_PAYED_DAYS = int(environ.get("VDS_MAX_PAYED_DAYS"))
VDS_EXPIRED_DAYS = int(environ.get("VDS_EXPIRED_DAYS"))

REDIS_HOST = environ.get("REDIS_HOST")
REDIS_PORT = int(environ.get("REDIS_PORT"))

MONERO_RPC_IP = environ.get("MONERO_RPC_IP")
MONERO_RPC_PORT = int(environ.get("MONERO_RPC_PORT"))
MONERO_RPC_USER = environ.get("MONERO_RPC_USER")
MONERO_RPC_PASSWORD = environ.get("MONERO_RPC_PASSWORD")

SUBNET_IPV4 = environ.get("SUBNET_IPV4")
