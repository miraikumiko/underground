from sqlalchemy import Column, Integer, String
from src.models import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    password = Column(String, nullable=False, unique=True, index=True)
