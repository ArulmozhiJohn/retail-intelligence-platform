from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.database import get_db
from app.services.inventory_service import InventoryService
from app.schemas.inventory import InventoryCreate, InventoryUpdate, InventoryResponse

router = APIRouter()


@router.get("/summary")
async def get_inventory_summary(db: AsyncSession = Depends(get_db)):
    return await InventoryService.get_summary(db)


@router.get("/low-stock", response_model=List[InventoryResponse])
async def get_low_stock(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await InventoryService.get_low_stock(db, skip=skip, limit=limit)


@router.get("/out-of-stock", response_model=List[InventoryResponse])
async def get_out_of_stock(db: AsyncSession = Depends(get_db)):
    return await InventoryService.get_out_of_stock(db)


@router.get("/store/{store_id}", response_model=List[InventoryResponse])
async def get_store_inventory(
    store_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await InventoryService.get_by_store(db, store_id, skip=skip, limit=limit)


@router.get("/store/{store_id}/product/{product_id}", response_model=InventoryResponse)
async def get_inventory_item(store_id: str, product_id: str, db: AsyncSession = Depends(get_db)):
    item = await InventoryService.get_by_store_and_product(db, store_id, product_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    return item


@router.post("/", response_model=InventoryResponse, status_code=201)
async def create_inventory(data: InventoryCreate, db: AsyncSession = Depends(get_db)):
    existing = await InventoryService.get_by_store_and_product(db, data.store_id, data.product_id)
    if existing:
        raise HTTPException(status_code=400, detail="Inventory record already exists for this store/product")
    return await InventoryService.create(db, data)


@router.patch("/{inventory_id}", response_model=InventoryResponse)
async def update_inventory(inventory_id: str, data: InventoryUpdate, db: AsyncSession = Depends(get_db)):
    item = await InventoryService.update(db, inventory_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    return item