from sqlalchemy import Column, Integer, String
from src.models import Base


class Node(Base):
    __tablename__ = "node"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, nullable=False, unique=True, index=True)
    cores = Column(Integer, nullable=False)
    cores_available = Column(Integer, nullable=False)
    ram = Column(Integer, nullable=False)
    ram_available = Column(Integer, nullable=False)
    disk_type = Column(String, nullable=False)
    disk_size = Column(Integer, nullable=False)
    disk_size_available = Column(Integer, nullable=False)
    location = Column(String, nullable=False)
