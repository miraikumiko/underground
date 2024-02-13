from dotenv import load_dotenv
from os import environ
from src.utils import int_void_convertion, void_convertion

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
PORT = int_void_convertion(environ.get("PORT"))
LOG_FILE = void_convertion(environ.get("LOG_FILE"))

# Security
SECRET = environ.get("SECRET")
TOKEN_LIFETIME = int_void_convertion(environ.get("TOKEN_LIFETIME"))

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
REDIS_PASSWORD = void_convertion(environ.get("REDIS_PASSWORD"))

# SMTP
SMTP_HOST = environ.get("SMTP_HOST")
SMTP_PORT = int_void_convertion(environ.get("SMTP_PORT"))
SMTP_USER = environ.get("SMTP_USER")
SMTP_PASSWORD = environ.get("SMTP_PASSWORD")
SMTP_SENDER = environ.get("SMTP_SENDER")

# RPC
RPC_KEY = environ.get("RPC_KEY")
