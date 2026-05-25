from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.database import get_db
from app.services.replenishment_service import ReplenishmentService
from app.schemas.replenishment import ReplenishmentCreate, ReplenishmentUpdate, ReplenishmentResponse

router = APIRouter()


@router.get("/summary")
async def get_replenishment_summary(db: AsyncSession = Depends(get_db)):
    return await ReplenishmentService.get_summary(db)


@router.get("/pending", response_model=List[ReplenishmentResponse])
async def get_pending(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await ReplenishmentService.get_pending(db, skip=skip, limit=limit)


@router.get("/store/{store_id}", response_model=List[ReplenishmentResponse])
async def get_store_replenishments(
    store_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await ReplenishmentService.get_by_store(db, store_id, skip=skip, limit=limit)


@router.post("/", response_model=ReplenishmentResponse, status_code=201)
async def create_replenishment(data: ReplenishmentCreate, db: AsyncSession = Depends(get_db)):
    return await ReplenishmentService.create(db, data)


@router.patch("/{replenishment_id}", response_model=ReplenishmentResponse)
async def update_replenishment(
    replenishment_id: str,
    data: ReplenishmentUpdate,
    db: AsyncSession = Depends(get_db),
):
    order = await ReplenishmentService.update(db, replenishment_id, data)
    if not order:
        raise HTTPException(status_code=404, detail="Replenishment order not found")
    return order


@router.post("/auto-trigger")
async def auto_trigger_replenishments(db: AsyncSession = Depends(get_db)):
    created = await ReplenishmentService.auto_trigger(db)
    return {
        "message": f"Auto-triggered {len(created)} replenishment orders",
        "count": len(created),
    }