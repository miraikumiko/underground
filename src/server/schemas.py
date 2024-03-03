from pydantic import BaseModel
from datetime import datetime


class ServerCreate(BaseModel):
    cores: int
    ram: int
    disk_type: str
    disk_size: int
    traffic: int
    location: str
    available: bool
    price: float


class ServerRead(BaseModel):
    id: int
    cores: int
    ram: int
    disk_type: str
    disk_size: int
    traffic: int
    location: str
    available: bool
    price: float


class ServerUpdate(BaseModel):
    cores: int = None
    ram: int = None
    disk_type: str = None
    disk_size: int = None
    traffic: int = None
    location: str = None
    available: bool = None
    price: float = None


class ActiveServerCreate(BaseModel):
    user_id: int
    server_id: int
    ipv4: str
    ipv6: str
    xml: str = None
    start_at: datetime = datetime.now()
    end_at: datetime


class ActiveServerRead(BaseModel):
    user_id: int
    server_id: int
    ipv4: str
    ipv6: str
    xml: str
    start_at: datetime
    end_at: datetime


class ActiveServerUpdate(BaseModel):
    user_id: int = None
    server_id: int = None
    ipv4: str = None
    ipv6: str = None
    xml: str = None
    start_at: datetime = None
    end_at: datetime = None


class ServerIPCreate(BaseModel):
    ip: str


class ServerIPRead(BaseModel):
    ip: str


class ServerIPUpdate(BaseModel):
    ip: str
