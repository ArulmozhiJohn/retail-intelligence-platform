from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=300)
    sku: str = Field(..., min_length=2, max_length=50)
    barcode: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    unit_price: Decimal = Field(..., gt=0)
    cost_price: Optional[Decimal] = None
    unit_of_measure: str = "each"
    is_active: bool = True
    is_perishable: bool = False
    shelf_life_days: Optional[int] = None
    reorder_point: int = 20
    reorder_quantity: int = 100


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    unit_price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
    reorder_point: Optional[int] = None
    reorder_quantity: Optional[int] = None


class ProductResponse(ProductBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ProductSummary(BaseModel):
    id: str
    name: str
    sku: str
    category: str
    brand: Optional[str] = None
    unit_price: Decimal
    is_active: bool

    model_config = {"from_attributes": True}