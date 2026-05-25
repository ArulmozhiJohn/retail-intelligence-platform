from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.db.database import get_db
from app.services.store_service import StoreService
from app.schemas.store import StoreCreate, StoreUpdate, StoreResponse, StoreSummary

router = APIRouter()


@router.get("/", response_model=List[StoreSummary])
async def get_stores(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    region: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    return await StoreService.get_all(db, skip=skip, limit=limit, region=region)


@router.get("/regions", response_model=List[str])
async def get_regions(db: AsyncSession = Depends(get_db)):
    return await StoreService.get_regions(db)


@router.get("/count")
async def get_store_count(db: AsyncSession = Depends(get_db)):
    count = await StoreService.get_count(db)
    return {"total_stores": count}


@router.get("/{store_id}", response_model=StoreResponse)
async def get_store(store_id: str, db: AsyncSession = Depends(get_db)):
    store = await StoreService.get_by_id(db, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store


@router.post("/", response_model=StoreResponse, status_code=201)
async def create_store(data: StoreCreate, db: AsyncSession = Depends(get_db)):
    existing = await StoreService.get_by_code(db, data.code)
    if existing:
        raise HTTPException(status_code=400, detail=f"Store code '{data.code}' already exists")
    return await StoreService.create(db, data)


@router.patch("/{store_id}", response_model=StoreResponse)
async def update_store(store_id: str, data: StoreUpdate, db: AsyncSession = Depends(get_db)):
    store = await StoreService.update(db, store_id, data)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store