from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    String,
    Text,
    DECIMAL,
    TIMESTAMP,
    ForeignKey
)
from datetime import datetime
from src.models import Base


class Server(Base):
    __tablename__ = "server"

    id = Column(Integer, primary_key=True, index=True)
    cores = Column(Integer, nullable=False)
    ram = Column(Integer, nullable=False)
    disk_type = Column(String, nullable=False)
    disk_size = Column(Integer, nullable=False)
    traffic = Column(Integer, nullable=False)
    location = Column(String, nullable=False)
    available = Column(Boolean, nullable=False, default=True)
    price = Column(DECIMAL(precision=12, scale=2), nullable=False)


class ActiveServer(Base):
    __tablename__ = "active_server"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    server_id = Column(Integer, ForeignKey('server.id'))
    ipv4 = Column(String, nullable=False, unique=True, index=True)
    ipv6 = Column(String, unique=True, index=True)
    xml = Column(Text, unique=True)
    start_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    end_at = Column(TIMESTAMP, nullable=False)


class ServerIP(Base):
    __tablename__ = "server_ip"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, nullable=False, unique=True, index=True)


class IPv4(Base):
    __tablename__ = "ipv4"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, nullable=False, unique=True, index=True)
    available = Column(Boolean, nullable=False, default=True)


class IPv6(Base):
    __tablename__ = "ipv6"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, nullable=False, unique=True, index=True)
    available = Column(Boolean, nullable=False, default=True)
