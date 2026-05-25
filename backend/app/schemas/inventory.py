from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class InventoryBase(BaseModel):
    store_id: str
    product_id: str
    quantity_on_hand: int = Field(default=0, ge=0)
    quantity_reserved: int = Field(default=0, ge=0)
    quantity_in_transit: int = Field(default=0, ge=0)
    reorder_point: int = 20
    max_stock_level: int = 500


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    quantity_on_hand: Optional[int] = None
    quantity_reserved: Optional[int] = None
    quantity_in_transit: Optional[int] = None
    reorder_point: Optional[int] = None
    max_stock_level: Optional[int] = None


class InventoryResponse(InventoryBase):
    id: str
    available_quantity: int
    stock_status: str
    last_restocked_at: Optional[datetime] = None
    last_sold_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class LowStockAlert(BaseModel):
    inventory_id: str
    store_id: str
    store_name: str
    product_id: str
    product_name: str
    sku: str
    quantity_on_hand: int
    reorder_point: int
    stock_status: str

    model_config = {"from_attributes": True}