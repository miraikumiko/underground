from pydantic import BaseModel
from datetime import datetime, timedelta


class ServerCreate(BaseModel):
    cores: int
    ram: int
    disk_type: str
    disk_size: int
    traffic: int
    location: str
    ipv4: str | None
    ipv6: str | None
    start_at: datetime = datetime.utcnow()
    end_at: datetime = datetime.utcnow() + timedelta(days=30)
    active: bool = True
    user_id: int


class ServerRead(BaseModel):
    id: int
    cores: int
    ram: int
    disk_type: str
    disk_size: int
    traffic: int
    location: str
    ipv4: str
    ipv6: str
    start_at: datetime
    end_at: datetime
    active: bool
    user_id: int


class ServerUpdate(BaseModel):
    cores: int = None
    ram: int = None
    disk_type: str = None
    disk_size: int = None
    traffic: int = None
    location: str = None
    ipv4: str = None
    ipv6: str = None
    start_at: datetime = None
    end_at: datetime = None
    active: bool = None
    user_id: int = None


class Specs(BaseModel):
    cores: int = 1
    ram: int = 1024
    disk_size: int = 32
    ipv4: bool = True
    month: int = 1
