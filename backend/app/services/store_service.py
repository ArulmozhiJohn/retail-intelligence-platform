from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.models.store import Store
from app.schemas.store import StoreCreate, StoreUpdate
from loguru import logger


class StoreService:

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100, region: Optional[str] = None) -> List[Store]:
        query = select(Store).where(Store.is_active == True)
        if region:
            query = query.where(Store.region == region)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, store_id: str) -> Optional[Store]:
        result = await db.execute(select(Store).where(Store.id == store_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_code(db: AsyncSession, code: str) -> Optional[Store]:
        result = await db.execute(select(Store).where(Store.code == code))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: StoreCreate) -> Store:
        store = Store(**data.model_dump())
        db.add(store)
        await db.flush()
        await db.refresh(store)
        logger.info(f"Store created: {store.code}")
        return store

    @staticmethod
    async def update(db: AsyncSession, store_id: str, data: StoreUpdate) -> Optional[Store]:
        store = await StoreService.get_by_id(db, store_id)
        if not store:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(store, field, value)
        await db.flush()
        await db.refresh(store)
        return store

    @staticmethod
    async def get_regions(db: AsyncSession) -> List[str]:
        result = await db.execute(select(Store.region).distinct().where(Store.is_active == True))
        return [r[0] for r in result.fetchall()]

    @staticmethod
    async def get_count(db: AsyncSession) -> int:
        result = await db.execute(select(func.count()).where(Store.is_active == True).select_from(Store))
        return result.scalar()