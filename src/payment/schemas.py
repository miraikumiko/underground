from pydantic import BaseModel


class Buy(BaseModel):
    vds_id: int


class Pay(BaseModel):
    server_id: int


class Upgrade(BaseModel):
    server_id: int
    vds_id: int


class VDSCreate(BaseModel):
    cores: int
    cores_desc: str
    ram: int
    ram_desc: str
    disk_type: str
    disk_size: int
    disk_desc: str
    ipv4: bool
    ipv6: bool
    traffic: int
    price: int


class VDSRead(BaseModel):
    id: int
    cores: int
    cores_desc: str
    ram: int
    ram_desc: str
    disk_type: str
    disk_size: int
    disk_desc: str
    ipv4: bool
    ipv6: bool
    traffic: int
    price: int


class VDSUpdate(BaseModel):
    cores: int
    cores_desc: str
    ram: int
    ram_desc: str
    disk_type: str
    disk_size: int
    disk_desc: str
    ipv4: bool
    ipv6: bool
    traffic: int
    price: int


class PromoCreate(BaseModel):
    code: str
    used: bool = False
    vds_id: int = 1
    days: int = 31


class PromoRead(BaseModel):
    id: int
    code: str
    used: bool
    vds_id: int
    days: int


class PromoUpdate(BaseModel):
    used: bool


class QRCode(BaseModel):
    uri: str
