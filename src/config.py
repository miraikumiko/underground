import json
from os import environ
from dotenv import load_dotenv

load_dotenv()

# App
HOST = environ.get("HOST")
PORT = environ.get("PORT")
LOG_FILE = environ.get("LOG_FILE")

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
MONERO_RECOVERY_COURSE = environ.get("MONERO_RECOVERY_COURSE")

# Subnet
SUBNET_IPV4 = environ.get("SUBNET_IPV4")
SUBNET_IPV6 = environ.get("SUBNET_IPV6")

# Type correction
PORT = int(PORT)
REDIS_PORT = int(REDIS_PORT)
MONERO_RPC_PORT = int(MONERO_RPC_PORT)
MONERO_RECOVERY_COURSE = float(MONERO_RECOVERY_COURSE)

# Read products
with open("products.json", 'r') as file:
    PRODUCTS = json.load(file)
