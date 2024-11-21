from sqlalchemy import Column, Integer, String, Boolean
from src.models import Base


class Promo(Base):
    __tablename__ = "promo"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, nullable=False, unique=True, index=True)
    used = Column(Boolean, nullable=False, default=False)
    vps_id = Column(Integer, nullable=False)
    days = Column(Integer, nullable=False)
