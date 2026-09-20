# app/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    card_id = Column(String, unique=True, index=True, nullable=False)  # tessera digitale
    points = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    category = Column(String, nullable=False)  # es. antipasti, primi, vini
    price = Column(Float, nullable=False)
    is_available = Column(Integer, default=1)  # 1=true, 0=false (semplice per ora)
    sort_order = Column(Integer, default=0)