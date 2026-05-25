from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StoreBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    code: str = Field(..., min_length=2, max_length=20)
    region: str
    city: str
    state: str
    country: str = "USA"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    store_type: str = "standard"
    is_active: bool = True


class StoreCreate(StoreBase):
    pass


class StoreUpdate(BaseModel):
    name: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    store_type: Optional[str] = None
    is_active: Optional[bool] = None


class StoreResponse(StoreBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class StoreSummary(BaseModel):
    id: str
    name: str
    code: str
    region: str
    city: str
    store_type: str
    is_active: bool

    model_config = {"from_attributes": True}