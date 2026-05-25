from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(300), nullable=False)
    sku = Column(String(50), unique=True, nullable=False)
    barcode = Column(String(100), unique=True)
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100))
    brand = Column(String(100))
    description = Column(Text)
    unit_price = Column(Numeric(10, 2), nullable=False)
    cost_price = Column(Numeric(10, 2))
    unit_of_measure = Column(String(20), default="each")
    weight_kg = Column(Float)
    is_active = Column(Boolean, default=True)
    is_perishable = Column(Boolean, default=False)
    shelf_life_days = Column(Integer)
    reorder_point = Column(Integer, default=20)
    reorder_quantity = Column(Integer, default=100)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    inventories = relationship("Inventory", back_populates="product")
    transactions = relationship("Transaction", back_populates="product")
    replenishments = relationship("Replenishment", back_populates="product")