from os import path
from starlette.config import Config

BASE_PATH = path.dirname(path.dirname(path.realpath(__file__)))

config = Config(f"{BASE_PATH}/.env")

HOST = config("HOST")
PORT = int(config("PORT"))

DB_PATH = config("DB_PATH")
IMAGES_PATH = config("IMAGES_PATH")

REGISTRATION = int(config("REGISTRATION"))
TOKEN_EXPIRY_DAYS = int(config("TOKEN_EXPIRY_DAYS"))

VDS_DAYS = int(config("VDS_DAYS"))
VDS_MAX_PAYED_DAYS = int(config("VDS_MAX_PAYED_DAYS"))
VDS_EXPIRED_DAYS = int(config("VDS_EXPIRED_DAYS"))

REDIS_HOST = config("REDIS_HOST")
REDIS_PORT = int(config("REDIS_PORT"))

MONERO_RPC_IP = config("MONERO_RPC_IP")
MONERO_RPC_PORT = int(config("MONERO_RPC_PORT"))
MONERO_RPC_USER = config("MONERO_RPC_USER")
MONERO_RPC_PASSWORD = config("MONERO_RPC_PASSWORD")
