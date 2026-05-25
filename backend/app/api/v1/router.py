from fastapi import APIRouter
from app.api.v1.endpoints import stores, products, inventory, transactions, replenishments, analytics, simulator

api_router = APIRouter()

api_router.include_router(stores.router,          prefix="/stores",          tags=["Stores"])
api_router.include_router(products.router,         prefix="/products",         tags=["Products"])
api_router.include_router(inventory.router,        prefix="/inventory",        tags=["Inventory"])
api_router.include_router(transactions.router,     prefix="/transactions",     tags=["Transactions"])
api_router.include_router(replenishments.router,   prefix="/replenishments",   tags=["Replenishments"])
api_router.include_router(analytics.router,        prefix="/analytics",        tags=["Analytics"])
api_router.include_router(simulator.router,        prefix="/simulator",        tags=["Simulator"])