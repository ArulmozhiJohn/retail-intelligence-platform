from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from datetime import datetime, timezone, timedelta
from app.db.database import get_db
from app.models.transaction import Transaction
from app.models.store import Store
from app.models.product import Product
from app.models.inventory import Inventory
from app.services.transaction_service import TransactionService
from app.services.inventory_service import InventoryService
from app.services.replenishment_service import ReplenishmentService

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard(
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
):
    tx_summary = await TransactionService.get_summary(db, hours=hours)
    inv_summary = await InventoryService.get_summary(db)
    rep_summary = await ReplenishmentService.get_summary(db)
    top_products = await TransactionService.get_top_products(db, hours=hours, limit=5)

    return {
        "period_hours": hours,
        "transactions": tx_summary,
        "inventory": inv_summary,
        "replenishments": rep_summary,
        "top_products": top_products,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/revenue-by-store")
async def revenue_by_store(
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    query = (
        select(
            Transaction.store_id,
            Store.name.label("store_name"),
            Store.region,
            func.sum(Transaction.total_amount).label("total_revenue"),
            func.count(Transaction.id).label("transaction_count"),
            func.sum(Transaction.quantity).label("units_sold"),
        )
        .join(Store, Transaction.store_id == Store.id)
        .where(Transaction.transacted_at >= since)
        .group_by(Transaction.store_id, Store.name, Store.region)
        .order_by(desc("total_revenue"))
        .limit(limit)
    )
    result = await db.execute(query)
    return [
        {
            "store_id": row.store_id,
            "store_name": row.store_name,
            "region": row.region,
            "total_revenue": float(row.total_revenue),
            "transaction_count": row.transaction_count,
            "units_sold": row.units_sold,
        }
        for row in result.fetchall()
    ]


@router.get("/revenue-by-category")
async def revenue_by_category(
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    query = (
        select(
            Product.category,
            func.sum(Transaction.total_amount).label("total_revenue"),
            func.sum(Transaction.quantity).label("units_sold"),
            func.count(Transaction.id).label("transaction_count"),
        )
        .join(Product, Transaction.product_id == Product.id)
        .where(Transaction.transacted_at >= since)
        .group_by(Product.category)
        .order_by(desc("total_revenue"))
    )
    result = await db.execute(query)
    return [
        {
            "category": row.category,
            "total_revenue": float(row.total_revenue),
            "units_sold": row.units_sold,
            "transaction_count": row.transaction_count,
        }
        for row in result.fetchall()
    ]


@router.get("/revenue-by-region")
async def revenue_by_region(
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    query = (
        select(
            Store.region,
            func.sum(Transaction.total_amount).label("total_revenue"),
            func.count(Transaction.id).label("transaction_count"),
        )
        .join(Store, Transaction.store_id == Store.id)
        .where(Transaction.transacted_at >= since)
        .group_by(Store.region)
        .order_by(desc("total_revenue"))
    )
    result = await db.execute(query)
    return [
        {
            "region": row.region,
            "total_revenue": float(row.total_revenue),
            "transaction_count": row.transaction_count,
        }
        for row in result.fetchall()
    ]


@router.get("/hourly-sales")
async def hourly_sales(
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    query = (
        select(
            func.date_trunc("hour", Transaction.transacted_at).label("hour"),
            func.sum(Transaction.total_amount).label("revenue"),
            func.count(Transaction.id).label("transactions"),
        )
        .where(Transaction.transacted_at >= since)
        .group_by("hour")
        .order_by("hour")
    )
    result = await db.execute(query)
    return [
        {
            "hour": row.hour.isoformat(),
            "revenue": float(row.revenue),
            "transactions": row.transactions,
        }
        for row in result.fetchall()
    ]