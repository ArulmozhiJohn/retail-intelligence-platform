from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.database import get_db
from app.models.store import Store
from app.models.product import Product
from app.models.inventory import Inventory

router = APIRouter()


@router.get("/status")
async def simulator_status(db: AsyncSession = Depends(get_db)):
    store_count = await db.execute(select(func.count()).select_from(Store))
    product_count = await db.execute(select(func.count()).select_from(Product))
    inventory_count = await db.execute(select(func.count()).select_from(Inventory))

    return {
        "stores_seeded": store_count.scalar(),
        "products_seeded": product_count.scalar(),
        "inventory_records": inventory_count.scalar(),
        "status": "ready" if store_count.scalar() > 0 else "not_seeded",
    }


@router.post("/seed")
async def seed_database(db: AsyncSession = Depends(get_db)):
    """
    Seed the database with 100 stores and 1000 products.
    Run this once before starting the simulator.
    """
    from app.services.simulator_service import SimulatorService
    result = await SimulatorService.seed_all(db)
    return result


@router.post("/run-cycle")
async def run_simulation_cycle(db: AsyncSession = Depends(get_db)):
    """
    Run one cycle of transactions manually.
    """
    from app.services.simulator_service import SimulatorService
    result = await SimulatorService.run_transaction_cycle(db)
    return result