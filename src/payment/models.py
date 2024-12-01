from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from src.models import Base


class VDS(Base):
    __tablename__ = "vds"

    id = Column(Integer, primary_key=True, index=True)
    cores = Column(Integer, nullable=False)
    cores_desc = Column(String, nullable=False)
    ram = Column(Integer, nullable=False)
    ram_desc = Column(String, nullable=False)
    disk_type = Column(String, nullable=False)
    disk_size = Column(Integer, nullable=False)
    disk_desc = Column(String, nullable=False)
    ipv4 = Column(Boolean, nullable=False)
    ipv6 = Column(Boolean, nullable=False)
    traffic = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)


class Promo(Base):
    __tablename__ = "promo"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, nullable=False, unique=True, index=True)
    used = Column(Boolean, nullable=False, default=False)
    vds_id = Column(Integer, ForeignKey("vds.id"), nullable=False)
    days = Column(Integer, nullable=False)
