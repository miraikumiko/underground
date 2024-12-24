from os import path
from starlette.config import Config

config = Config(".env")

BASE_PATH = path.dirname(path.dirname(path.realpath(__file__)))

HOST = config("HOST")
PORT = int(config("PORT"))

DB_PATH = config("DB_PATH")
IMAGES_PATH = config("IMAGES_PATH")

REGISTRATION = int(config("REGISTRATION"))

PAYMENT_TIME = int(config("PAYMENT_TIME"))
PAYMENT_LIMIT = int(config("PAYMENT_LIMIT"))

VDS_DAYS = int(config("VDS_DAYS"))
VDS_MAX_PAYED_DAYS = int(config("VDS_MAX_PAYED_DAYS"))
VDS_EXPIRED_DAYS = int(config("VDS_EXPIRED_DAYS"))

REDIS_HOST = config("REDIS_HOST")
REDIS_PORT = int(config("REDIS_PORT"))

MONERO_RPC_IP = config("MONERO_RPC_IP")
MONERO_RPC_PORT = int(config("MONERO_RPC_PORT"))
MONERO_RPC_USER = config("MONERO_RPC_USER")
MONERO_RPC_PASSWORD = config("MONERO_RPC_PASSWORD")

SUBNET_IPV4 = config("SUBNET_IPV4")
