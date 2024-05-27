from pydantic import BaseModel
from datetime import datetime, timedelta


class ServerCreate(BaseModel):
    cores: int
    ram: int
    disk_type: str
    disk_size: int
    traffic: int
    vnc_port: int
    ipv4: str | None
    ipv6: str | None
    start_at: datetime = datetime.utcnow()
    end_at: datetime = datetime.utcnow() + timedelta(days=30)
    active: bool = True
    user_id: int
    node_id: int


class ServerRead(BaseModel):
    id: int
    cores: int
    ram: int
    disk_type: str
    disk_size: int
    traffic: int
    vnc_port: int
    ipv4: str
    ipv6: str
    start_at: datetime
    end_at: datetime
    active: bool
    user_id: int
    node_id: int


class ServerUpdate(BaseModel):
    cores: int = None
    ram: int = None
    disk_type: str = None
    disk_size: int = None
    traffic: int = None
    vnc_port: int
    ipv4: str = None
    ipv6: str = None
    start_at: datetime = None
    end_at: datetime = None
    active: bool = None
    user_id: int = None
    node_id: int = None


class VPSInstall(BaseModel):
    server_id: int
    os: str


class VPSAction(BaseModel):
    server_id: int
    cmd: str


class IPCreate(BaseModel):
    ip: str
    available: bool = False


class IPRead(BaseModel):
    id: int
    ip: str
    available: bool


class IPUpdate(BaseModel):
    available: bool
