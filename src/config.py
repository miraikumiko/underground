from os import path
from starlette.config import Config

BASE_PATH = path.dirname(path.dirname(path.realpath(__file__)))

config = Config(f"{BASE_PATH}/.env")

HOST = config("HOST")
PORT = config("PORT", cast=int)

DB_PATH = config("DB_PATH")
IMAGES_PATH = config("IMAGES_PATH")

REGISTRATION = config("REGISTRATION", cast=bool)
TOKEN_EXPIRY_DAYS = config("TOKEN_EXPIRY_DAYS", cast=int)

VDS_DAYS = config("VDS_DAYS", cast=int)
VDS_MAX_PAYED_DAYS = config("VDS_MAX_PAYED_DAYS", cast=int)
VDS_EXPIRED_DAYS = config("VDS_EXPIRED_DAYS", cast=int)

REDIS_HOST = config("REDIS_HOST")
REDIS_PORT = config("REDIS_PORT", cast=int)

MONERO_RPC_IP = config("MONERO_RPC_IP")
MONERO_RPC_PORT = config("MONERO_RPC_PORT", cast=int)
MONERO_RPC_USER = config("MONERO_RPC_USER")
MONERO_RPC_PASSWORD = config("MONERO_RPC_PASSWORD")
