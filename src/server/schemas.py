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
    vds_id: int
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
    vds_id: int
    node_id: int


class ServerUpdate(BaseModel):
    ipv4: str = None
    ipv6: str = None
    vnc_port: int = None
    start_at: datetime = None
    end_at: datetime = None
    is_active: bool = None
    user_id: int = None
    vds_id: int = None
    node_id: int = None

    def rm_none_attrs(self):
        return {k: v for k, v in self.model_dump().items() if v is not None}
