from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.database import Base

class Store(Base):
    __tablename__ = "stores"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    region = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    country = Column(String(100), default="USA")
    latitude = Column(Float)
    longitude = Column(Float)
    store_type = Column(String(50), default="standard")  # standard, flagship, express
    is_active = Column(Boolean, default=True)
    opened_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    inventories = relationship("Inventory", back_populates="store")
    transactions = relationship("Transaction", back_populates="store")
    replenishments = relationship("Replenishment", back_populates="store")