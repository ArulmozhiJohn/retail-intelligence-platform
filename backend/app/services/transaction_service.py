from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from app.models.transaction import Transaction
from app.models.inventory import Inventory
from app.schemas.transaction import TransactionCreate
from loguru import logger


class TransactionService:

    @staticmethod
    async def create(db: AsyncSession, data: TransactionCreate) -> Transaction:
        transaction = Transaction(**data.model_dump())
        db.add(transaction)

        # Adjust inventory
        inv_result = await db.execute(
            select(Inventory).where(
                and_(
                    Inventory.store_id == data.store_id,
                    Inventory.product_id == data.product_id,
                )
            )
        )
        inventory = inv_result.scalar_one_or_none()
        if inventory:
            if data.transaction_type == "sale":
                inventory.quantity_on_hand = max(0, inventory.quantity_on_hand - data.quantity)
                inventory.last_sold_at = datetime.now(timezone.utc)
            elif data.transaction_type == "return":
                inventory.quantity_on_hand += data.quantity
            inventory.updated_at = datetime.now(timezone.utc)

        await db.flush()
        await db.refresh(transaction)
        return transaction

    @staticmethod
    async def get_by_store(
        db: AsyncSession,
        store_id: str,
        skip: int = 0,
        limit: int = 100,
        hours: int = 24,
    ) -> List[Transaction]:
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        query = (
            select(Transaction)
            .where(and_(Transaction.store_id == store_id, Transaction.transacted_at >= since))
            .options(selectinload(Transaction.product))
            .order_by(desc(Transaction.transacted_at))
            .offset(skip).limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_recent(db: AsyncSession, limit: int = 50) -> List[Transaction]:
        query = (
            select(Transaction)
            .options(selectinload(Transaction.store), selectinload(Transaction.product))
            .order_by(desc(Transaction.transacted_at))
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_summary(db: AsyncSession, hours: int = 24) -> dict:
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        base = select(Transaction).where(Transaction.transacted_at >= since)

        total_tx = await db.execute(select(func.count()).select_from(base.subquery()))
        total_rev = await db.execute(select(func.sum(Transaction.total_amount)).where(Transaction.transacted_at >= since))
        total_units = await db.execute(select(func.sum(Transaction.quantity)).where(Transaction.transacted_at >= since))

        total_tx_val = total_tx.scalar() or 0
        total_rev_val = float(total_rev.scalar() or 0)
        total_units_val = total_units.scalar() or 0

        return {
            "period_hours": hours,
            "total_transactions": total_tx_val,
            "total_revenue": round(total_rev_val, 2),
            "total_units_sold": total_units_val,
            "average_transaction_value": round(total_rev_val / total_tx_val, 2) if total_tx_val > 0 else 0,
        }

    @staticmethod
    async def get_top_products(db: AsyncSession, hours: int = 24, limit: int = 10) -> List[dict]:
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        query = (
            select(
                Transaction.product_id,
                func.sum(Transaction.quantity).label("total_units"),
                func.sum(Transaction.total_amount).label("total_revenue"),
                func.count(Transaction.id).label("transaction_count"),
            )
            .where(Transaction.transacted_at >= since)
            .group_by(Transaction.product_id)
            .order_by(desc("total_revenue"))
            .limit(limit)
        )
        result = await db.execute(query)
        return [
            {
                "product_id": row.product_id,
                "total_units": row.total_units,
                "total_revenue": float(row.total_revenue),
                "transaction_count": row.transaction_count,
            }
            for row in result.fetchall()
        ]