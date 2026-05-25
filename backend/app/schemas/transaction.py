from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class TransactionBase(BaseModel):
    store_id: str
    product_id: str
    transaction_type: str = "sale"
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)
    total_amount: Decimal
    discount_amount: Decimal = Decimal("0")
    tax_amount: Decimal = Decimal("0")
    payment_method: Optional[str] = None
    pos_terminal: Optional[str] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    id: str
    transacted_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionSummary(BaseModel):
    total_transactions: int
    total_revenue: float
    total_units_sold: int
    average_transaction_value: float
    top_payment_method: Optional[str] = None