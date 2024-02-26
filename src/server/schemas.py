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
    cores: int
    ram: int
    disk_type: str
    disk_size: int
    traffic: int
    location: str
    avaible: bool
    price: float


class ServerUpdate(BaseModel):
    cores: int
    ram: int
    disk_type: str
    disk_size: int
    traffic: int
    location: str
    avaible: bool
    price: float


class ActiveServerCreate(BaseModel):
    user_id: int
    server_id: int
    ipv4: IPvAnyAddress
    ipv6: IPvAnyAddress
    xml: str
    start_at: datetime
    end_at: datetime


class ActiveServerRead(BaseModel):
    user_id: int
    server_id: int
    ipv4: IPvAnyAddress
    ipv6: IPvAnyAddress
    xml: str
    start_at: datetime
    end_at: datetime


class ActiveServerUpdate(BaseModel):
    user_id: int
    server_id: int
    ipv4: IPvAnyAddress
    ipv6: IPvAnyAddress
    xml: str
    start_at: datetime
    end_at: datetime


class ActiveServerBuy(BaseModel):
    server_id: int
    payment_id: int
    month: int


class ActiveServerPay(BaseModel):
    active_server_id: int
    payment_id: int
    month: int


class ActiveServerAction(BaseModel):
    active_server_id: int
    action: str
