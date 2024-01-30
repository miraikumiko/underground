from pydantic import BaseModel
from datetime import datetime


class ServerCreate(BaseModel):
    cores: int
    ram: int
    disk: int
    traffic: int
    location: str
    avaible: bool
    price: float


class ServerRead(BaseModel):
    cores: int
    ram: int
    disk: int
    traffic: int
    location: str
    avaible: bool
    price: float


class ServerUpdate(BaseModel):
    cores: int
    ram: int
    disk: int
    traffic: int
    location: str
    avaible: bool
    price: float


class ActiveServerCreate(BaseModel):
    user_id: int
    server_id: int
    iso: str
    ipv4: str
    ipv6: str
    start_at: datetime
    end_at: datetime


class ActiveServerRead(BaseModel):
    user_id: int
    server_id: int
    iso: str
    ipv4: str
    ipv6: str
    start_at: datetime
    end_at: datetime


class ActiveServerUpdate(BaseModel):
    user_id: int
    server_id: int
    iso: str
    ipv4: str
    ipv6: str
    start_at: datetime
    end_at: datetime


class ServerAction(BaseModel):
    server_id: int
    action: str


class ServerCheckout(BaseModel):
    server_id: int
    method: str
