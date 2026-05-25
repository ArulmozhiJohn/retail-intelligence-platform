from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey, Numeric, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.db.database import Base

class TransactionType(str, enum.Enum):
    SALE = "sale"
    RETURN = "return"
    ADJUSTMENT = "adjustment"
    TRANSFER = "transfer"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    store_id = Column(String, ForeignKey("stores.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    transaction_type = Column(String(20), default="sale")
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    payment_method = Column(String(50))
    customer_id = Column(String(100))
    cashier_id = Column(String(100))
    pos_terminal = Column(String(50))
    notes = Column(String(500))
    transacted_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    store = relationship("Store", back_populates="transactions")
    product = relationship("Product", back_populates="transactions")