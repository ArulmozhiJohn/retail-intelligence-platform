from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ReplenishmentBase(BaseModel):
    store_id: str
    product_id: str
    requested_quantity: int = Field(..., gt=0)
    priority: str = "normal"
    trigger_reason: Optional[str] = None
    notes: Optional[str] = None


class ReplenishmentCreate(ReplenishmentBase):
    pass


class ReplenishmentUpdate(BaseModel):
    status: Optional[str] = None
    approved_quantity: Optional[int] = None
    fulfilled_quantity: Optional[int] = None
    expected_delivery_at: Optional[datetime] = None
    notes: Optional[str] = None


class ReplenishmentResponse(ReplenishmentBase):
    id: str
    status: str
    approved_quantity: Optional[int] = None
    fulfilled_quantity: Optional[int] = None
    estimated_cost: Optional[Decimal] = None
    expected_delivery_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}