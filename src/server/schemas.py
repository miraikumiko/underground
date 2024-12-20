from pydantic import BaseModel
from datetime import datetime, timedelta, UTC


class ServerCreate(BaseModel):
    vnc_port: int
    start_at: datetime = datetime.now(UTC)
    end_at: datetime = datetime.now(UTC) + timedelta(days=31)
    is_active: bool = True
    in_upgrade: bool = False
    user_id: int
    vds_id: int
    node_id: int


class ServerRead(BaseModel):
    id: int
    vnc_port: int
    start_at: datetime
    end_at: datetime
    is_active: bool
    in_upgrade: bool
    user_id: int
    vds_id: int
    node_id: int


class ServerUpdate(BaseModel):
    vnc_port: int = None
    start_at: datetime = None
    end_at: datetime = None
    is_active: bool = None
    in_upgrade: bool = None
    user_id: int = None
    vds_id: int = None
    node_id: int = None

    def rm_none_attrs(self):
        return {k: v for k, v in self.model_dump().items() if v is not None}
