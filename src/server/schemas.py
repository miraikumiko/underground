from pydantic import BaseModel
from datetime import datetime, timedelta, UTC


class ServerCreate(BaseModel):
    ipv4: str | None
    ipv6: str | None
    vnc_port: int
    start_at: datetime = datetime.now(UTC)
    end_at: datetime = datetime.now(UTC) + timedelta(days=31)
    is_active: bool = True
    user_id: int
    vps_id: int
    node_id: int


class ServerRead(BaseModel):
    id: int
    ipv4: str
    ipv6: str
    vnc_port: int
    start_at: datetime
    end_at: datetime
    is_active: bool
    user_id: int
    vps_id: int
    node_id: int


class ServerUpdate(BaseModel):
    ipv4: str = None
    ipv6: str = None
    vnc_port: int
    start_at: datetime = None
    end_at: datetime = None
    is_active: bool = None
    user_id: int = None
    vps_id: int
    node_id: int = None


class VPSInstall(BaseModel):
    server_id: int
    os: str


class VPSAction(BaseModel):
    server_id: int
    cmd: str


class IPRead(BaseModel):
    id: int
    ip: str
    available: bool


class IPUpdate(BaseModel):
    available: bool
