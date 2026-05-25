from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timezone
from app.models.inventory import Inventory
from app.models.store import Store
from app.models.product import Product
from app.schemas.inventory import InventoryCreate, InventoryUpdate
from loguru import logger


class InventoryService:

    @staticmethod
    async def get_by_store(db: AsyncSession, store_id: str, skip: int = 0, limit: int = 100) -> List[Inventory]:
        query = (
            select(Inventory)
            .where(Inventory.store_id == store_id)
            .options(selectinload(Inventory.product))
            .offset(skip).limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_by_store_and_product(db: AsyncSession, store_id: str, product_id: str) -> Optional[Inventory]:
        result = await db.execute(
            select(Inventory).where(
                and_(Inventory.store_id == store_id, Inventory.product_id == product_id)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: InventoryCreate) -> Inventory:
        inventory = Inventory(**data.model_dump())
        db.add(inventory)
        await db.flush()
        await db.refresh(inventory)
        return inventory

    @staticmethod
    async def update(db: AsyncSession, inventory_id: str, data: InventoryUpdate) -> Optional[Inventory]:
        result = await db.execute(select(Inventory).where(Inventory.id == inventory_id))
        inventory = result.scalar_one_or_none()
        if not inventory:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(inventory, field, value)
        inventory.updated_at = datetime.now(timezone.utc)
        await db.flush()
        await db.refresh(inventory)
        return inventory

    @staticmethod
    async def adjust_stock(db: AsyncSession, store_id: str, product_id: str, quantity_delta: int) -> Optional[Inventory]:
        inventory = await InventoryService.get_by_store_and_product(db, store_id, product_id)
        if not inventory:
            return None
        inventory.quantity_on_hand = max(0, inventory.quantity_on_hand + quantity_delta)
        if quantity_delta < 0:
            inventory.last_sold_at = datetime.now(timezone.utc)
        else:
            inventory.last_restocked_at = datetime.now(timezone.utc)
        inventory.updated_at = datetime.now(timezone.utc)
        await db.flush()
        await db.refresh(inventory)
        return inventory

    @staticmethod
    async def get_low_stock(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Inventory]:
        query = (
            select(Inventory)
            .where(Inventory.quantity_on_hand <= Inventory.reorder_point)
            .options(selectinload(Inventory.store), selectinload(Inventory.product))
            .offset(skip).limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_out_of_stock(db: AsyncSession) -> List[Inventory]:
        query = (
            select(Inventory)
            .where(Inventory.quantity_on_hand == 0)
            .options(selectinload(Inventory.store), selectinload(Inventory.product))
        )
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_summary(db: AsyncSession) -> dict:
        total = await db.execute(select(func.count()).select_from(Inventory))
        out_of_stock = await db.execute(select(func.count()).where(Inventory.quantity_on_hand == 0).select_from(Inventory))
        low_stock = await db.execute(select(func.count()).where(
            and_(Inventory.quantity_on_hand > 0, Inventory.quantity_on_hand <= Inventory.reorder_point)
        ).select_from(Inventory))
        total_units = await db.execute(select(func.sum(Inventory.quantity_on_hand)))
        return {
            "total_inventory_records": total.scalar(),
            "out_of_stock_count": out_of_stock.scalar(),
            "low_stock_count": low_stock.scalar(),
            "total_units_on_hand": total_units.scalar() or 0,
        }