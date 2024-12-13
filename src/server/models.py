from sqlalchemy import Column, Integer, Boolean, String, TIMESTAMP, ForeignKey
from datetime import datetime
from src.models import Base


class Server(Base):
    __tablename__ = "server"

    id = Column(Integer, primary_key=True, index=True)
    ipv4 = Column(String)
    ipv6 = Column(String)
    vnc_port = Column(Integer, nullable=False)
    start_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    end_at = Column(TIMESTAMP, nullable=False)
    is_active = Column(Boolean, nullable=False)
    in_upgrade = Column(Boolean, nullable=False, default=False)
    vds_id = Column(Integer, ForeignKey("vds.id"), nullable=False)
    node_id = Column(Integer, ForeignKey("node.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
