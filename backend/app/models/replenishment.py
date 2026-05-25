from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.database import Base

class Replenishment(Base):
    __tablename__ = "replenishments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    store_id = Column(String, ForeignKey("stores.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    requested_quantity = Column(Integer, nullable=False)
    approved_quantity = Column(Integer)
    fulfilled_quantity = Column(Integer)
    status = Column(String(30), default="pending")  # pending, approved, shipped, delivered, cancelled
    priority = Column(String(20), default="normal")  # low, normal, high, critical
    trigger_reason = Column(String(100))  # low_stock, out_of_stock, scheduled, manual
    estimated_cost = Column(Numeric(12, 2))
    supplier_id = Column(String(100))
    expected_delivery_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    store = relationship("Store", back_populates="replenishments")
    product = relationship("Product", back_populates="replenishments")