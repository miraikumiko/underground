from pydantic import BaseModel, IPvAnyAddress
from datetime import datetime


class ServerCreate(BaseModel):
    cores: int
    ram: int
    disk_type: str
    disk_size: int
    traffic: int
    location: str
    avaible: bool
    price: float


class ServerRead(BaseModel):
    id: int
    cores: int
    ram: int
    disk_type: str
    disk_size: int
    traffic: int
    location: str
    avaible: bool
    price: float


class ServerUpdate(BaseModel):
    id: int
    cores: int
    ram: int
    disk_type: str
    disk_size: int
    traffic: int
    location: str
    avaible: bool
    price: float


class ServerDelete(BaseModel):
    id: int


class ActiveServerCreate(BaseModel):
    user_id: int
    server_id: int
    ipv4: IPvAnyAddress
    ipv6: IPvAnyAddress
    xml: str
    start_at: datetime
    end_at: datetime


class ActiveServerRead(BaseModel):
    id: int
    user_id: int
    server_id: int
    ipv4: IPvAnyAddress
    ipv6: IPvAnyAddress
    xml: str
    start_at: datetime
    end_at: datetime


class ActiveServerUpdate(BaseModel):
    id: int
    user_id: int
    server_id: int
    ipv4: IPvAnyAddress
    ipv6: IPvAnyAddress
    xml: str
    start_at: datetime
    end_at: datetime


class ActiveServerDelete(BaseModel):
    id: int


class ActiveServerAction(BaseModel):
    active_server_id: int
    action: str


class ServerIPCreate(BaseModel):
    ip: IPvAnyAddress


class ServerIPRead(BaseModel):
    ip: IPvAnyAddress


class ServerIPUpdate(BaseModel):
    ip: IPvAnyAddress
