from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.database import get_db
from app.services.transaction_service import TransactionService
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionSummary

router = APIRouter()


@router.get("/recent", response_model=List[TransactionResponse])
async def get_recent_transactions(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    return await TransactionService.get_recent(db, limit=limit)


@router.get("/summary")
async def get_transaction_summary(
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
):
    return await TransactionService.get_summary(db, hours=hours)


@router.get("/top-products")
async def get_top_products(
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    return await TransactionService.get_top_products(db, hours=hours, limit=limit)


@router.get("/store/{store_id}", response_model=List[TransactionResponse])
async def get_store_transactions(
    store_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
):
    return await TransactionService.get_by_store(db, store_id, skip=skip, limit=limit, hours=hours)


@router.post("/", response_model=TransactionResponse, status_code=201)
async def create_transaction(data: TransactionCreate, db: AsyncSession = Depends(get_db)):
    return await TransactionService.create(db, data)