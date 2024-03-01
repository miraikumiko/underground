from dotenv import load_dotenv
from os import environ


load_dotenv()


# Main
SERVICE_NAME = environ.get("SERVICE_NAME")
DOMAIN = environ.get("DOMAIN")
ONION_DOMAIN = environ.get("ONION_DOMAIN")
I2P_DOMAIN = environ.get("I2P_DOMAIN")

# App
MODE = environ.get("MODE")
SOCKET = environ.get("SOCKET")
HOST = environ.get("HOST")
PORT = environ.get("PORT")
LOG_FILE = environ.get("LOG_FILE")

# Security
SECRET = environ.get("SECRET")
TOKEN_LIFETIME = environ.get("TOKEN_LIFETIME")

# Database
DB_TYPE = environ.get("DB_TYPE")
DB_HOST = environ.get("DB_HOST")
DB_PORT = environ.get("DB_PORT")
DB_DATABASE = environ.get("DB_DATABASE")
DB_USERNAME = environ.get("DB_USERNAME")
DB_PASSWORD = environ.get("DB_PASSWORD")

# Redis
REDIS_HOST = environ.get("REDIS_HOST")
REDIS_PORT = environ.get("REDIS_PORT")
REDIS_PASSWORD = environ.get("REDIS_PASSWORD")

# SMTP
SMTP_HOST = environ.get("SMTP_HOST")
SMTP_PORT = environ.get("SMTP_PORT")
SMTP_USER = environ.get("SMTP_USER")
SMTP_PASSWORD = environ.get("SMTP_PASSWORD")
SMTP_SENDER = environ.get("SMTP_SENDER")

# QEMU
QEMU_PORT = environ.get("QEMU_PORT")

# RPC
RPC_SERVER_PORT = environ.get("RPC_SERVER_PORT")
RPC_SERVER_KEY = environ.get("RPC_SERVER_KEY")

# Monero
MONERO_RPC_IP = environ.get("MONERO_RPC_IP")
MONERO_RPC_PORT = environ.get("MONERO_RPC_PORT")
MONERO_RPC_USER = environ.get("MONERO_RPC_USER")
MONERO_RPC_PASSWORD = environ.get("MONERO_RPC_PASSWORD")


# Type correction

PORT = int(PORT)
TOKEN_LIFETIME = None if TOKEN_LIFETIME == '' else int(TOKEN_LIFETIME)
DB_PORT = int(DB_PORT)
REDIS_PORT = int(REDIS_PORT)
SMTP_PORT = int(SMTP_PORT)
QEMU_PORT = int(QEMU_PORT)
RPC_SERVER_PORT = int(RPC_SERVER_PORT)
MONERO_RPC_PORT = int(MONERO_RPC_PORT)
