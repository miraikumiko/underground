from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    String,
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
    disk = Column(Integer, nullable=False)
    traffic = Column(Integer, nullable=False)
    location = Column(String, nullable=False)
    avaible = Column(Boolean, nullable=False, default=True)
    price = Column(DECIMAL(precision=12, scale=2), nullable=False)


class ActiveServer(Base):
    __tablename__ = "active_server"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    server_id = Column(Integer, ForeignKey('server.id'))
    iso = Column(String, nullable=True, index=True)
    ipv4 = Column(String, nullable=False, unique=True, index=True)
    ipv6 = Column(String, nullable=True, unique=True, index=True)
    start_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    end_at = Column(TIMESTAMP, nullable=False)
