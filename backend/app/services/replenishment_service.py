from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from app.models.replenishment import Replenishment
from app.models.inventory import Inventory
from app.models.product import Product
from app.schemas.replenishment import ReplenishmentCreate, ReplenishmentUpdate
from app.core.config import settings
from loguru import logger


class ReplenishmentService:

    @staticmethod
    async def create(db: AsyncSession, data: ReplenishmentCreate) -> Replenishment:
        replenishment = Replenishment(**data.model_dump())
        replenishment.status = "pending"
        db.add(replenishment)
        await db.flush()
        await db.refresh(replenishment)
        logger.info(f"Replenishment created for store {data.store_id}, product {data.product_id}")
        return replenishment

    @staticmethod
    async def update(db: AsyncSession, replenishment_id: str, data: ReplenishmentUpdate) -> Optional[Replenishment]:
        result = await db.execute(select(Replenishment).where(Replenishment.id == replenishment_id))
        replenishment = result.scalar_one_or_none()
        if not replenishment:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(replenishment, field, value)
        if data.status == "delivered":
            replenishment.delivered_at = datetime.now(timezone.utc)
        await db.flush()
        await db.refresh(replenishment)
        return replenishment

    @staticmethod
    async def get_pending(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Replenishment]:
        query = (
            select(Replenishment)
            .where(Replenishment.status.in_(["pending", "approved", "shipped"]))
            .options(selectinload(Replenishment.store), selectinload(Replenishment.product))
            .order_by(desc(Replenishment.created_at))
            .offset(skip).limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_by_store(db: AsyncSession, store_id: str, skip: int = 0, limit: int = 100) -> List[Replenishment]:
        query = (
            select(Replenishment)
            .where(Replenishment.store_id == store_id)
            .options(selectinload(Replenishment.product))
            .order_by(desc(Replenishment.created_at))
            .offset(skip).limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def auto_trigger(db: AsyncSession) -> List[Replenishment]:
        """
        Scan all inventory and auto-create replenishment orders
        for items below reorder point with no pending order.
        """
        low_stock_query = select(Inventory).where(
            Inventory.quantity_on_hand <= Inventory.reorder_point
        ).options(selectinload(Inventory.product))
        low_stock_result = await db.execute(low_stock_query)
        low_stock_items = low_stock_result.scalars().all()

        created = []
        for item in low_stock_items:
            # Check if a pending replenishment already exists
            existing = await db.execute(
                select(Replenishment).where(
                    and_(
                        Replenishment.store_id == item.store_id,
                        Replenishment.product_id == item.product_id,
                        Replenishment.status.in_(["pending", "approved", "shipped"]),
                    )
                )
            )
            if existing.scalar_one_or_none():
                continue

            # Determine priority
            if item.quantity_on_hand == 0:
                priority = "critical"
                reason = "out_of_stock"
            elif item.quantity_on_hand <= settings.CRITICAL_STOCK_THRESHOLD:
                priority = "high"
                reason = "critical_stock"
            else:
                priority = "normal"
                reason = "low_stock"

            reorder_qty = (item.product.reorder_quantity if item.product else 100) * settings.REORDER_MULTIPLIER

            new_order = Replenishment(
                store_id=item.store_id,
                product_id=item.product_id,
                requested_quantity=reorder_qty,
                priority=priority,
                trigger_reason=reason,
                status="pending",
            )
            db.add(new_order)
            created.append(new_order)

        if created:
            await db.flush()
            logger.info(f"Auto-triggered {len(created)} replenishment orders")

        return created

    @staticmethod
    async def get_summary(db: AsyncSession) -> dict:
        statuses = ["pending", "approved", "shipped", "delivered", "cancelled"]
        summary = {}
        for status in statuses:
            result = await db.execute(
                select(func.count()).where(Replenishment.status == status).select_from(Replenishment)
            )
            summary[status] = result.scalar()
        return summary