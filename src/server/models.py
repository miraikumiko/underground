from sqlalchemy import Column, Integer, Boolean, String, TIMESTAMP, ForeignKey
from datetime import datetime
from src.models import Base


class Server(Base):
    __tablename__ = "server"

    id = Column(Integer, primary_key=True, index=True)
    cores = Column(Integer, nullable=False)
    ram = Column(Integer, nullable=False)
    disk_type = Column(String, nullable=False)
    disk_size = Column(Integer, nullable=False)
    ipv4 = Column(String, unique=True, index=True)
    ipv6 = Column(String, unique=True, index=True)
    traffic = Column(Integer, nullable=False)
    start_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    end_at = Column(TIMESTAMP, nullable=False)
    active = Column(Boolean, nullable=False, index=True, default=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    node_id = Column(Integer, ForeignKey("node.id"), nullable=False)


class IPv4(Base):
    __tablename__ = "ipv4"

    ip = Column(String, primary_key=True, nullable=False, unique=True, index=True)
    available = Column(Boolean, nullable=False, default=True)


class IPv6(Base):
    __tablename__ = "ipv6"

    ip = Column(String, primary_key=True, nullable=False, unique=True, index=True)
    available = Column(Boolean, nullable=False, default=True)
