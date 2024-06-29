from sqlalchemy import Column, Integer, String, Boolean
from src.models import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, index=True, default=True)
