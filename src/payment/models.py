from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    String,
    ForeignKey
)
from src.models import Base


class Payment(Base):
    __tablename__ = "payment"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), index=True)
    server_id = Column(Integer, ForeignKey('server.id'), index=True)
    active_server_id = Column(Integer, ForeignKey('active_server.id'), nullable=True, index=True)
    payment_id = Column(Integer, nullable=False, unique=True, index=True)
    amount = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False, index=True, default=True)


class Discount(Base):
    __tablename__ = "discount"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), index=True)
    discount = Column(Integer, nullable=False)
