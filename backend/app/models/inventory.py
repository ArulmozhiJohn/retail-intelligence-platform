from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.database import Base

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    store_id = Column(String, ForeignKey("stores.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    quantity_on_hand = Column(Integer, default=0)
    quantity_reserved = Column(Integer, default=0)
    quantity_in_transit = Column(Integer, default=0)
    reorder_point = Column(Integer, default=20)
    max_stock_level = Column(Integer, default=500)
    last_restocked_at = Column(DateTime(timezone=True))
    last_sold_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    store = relationship("Store", back_populates="inventories")
    product = relationship("Product", back_populates="inventories")

    @property
    def available_quantity(self):
        return self.quantity_on_hand - self.quantity_reserved

    @property
    def stock_status(self):
        if self.quantity_on_hand == 0:
            return "out_of_stock"
        elif self.quantity_on_hand <= 10:
            return "critical"
        elif self.quantity_on_hand <= self.reorder_point:
            return "low"
        else:
            return "healthy"