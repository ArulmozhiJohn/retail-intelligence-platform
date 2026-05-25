from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Optional
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from loguru import logger


class ProductService:

    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Product]:
        query = select(Product).where(Product.is_active == True)
        if category:
            query = query.where(Product.category == category)
        if search:
            query = query.where(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.sku.ilike(f"%{search}%"),
                    Product.brand.ilike(f"%{search}%"),
                )
            )
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, product_id: str) -> Optional[Product]:
        result = await db.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_sku(db: AsyncSession, sku: str) -> Optional[Product]:
        result = await db.execute(select(Product).where(Product.sku == sku))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: ProductCreate) -> Product:
        product = Product(**data.model_dump())
        db.add(product)
        await db.flush()
        await db.refresh(product)
        logger.info(f"Product created: {product.sku}")
        return product

    @staticmethod
    async def update(db: AsyncSession, product_id: str, data: ProductUpdate) -> Optional[Product]:
        product = await ProductService.get_by_id(db, product_id)
        if not product:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(product, field, value)
        await db.flush()
        await db.refresh(product)
        return product

    @staticmethod
    async def get_categories(db: AsyncSession) -> List[str]:
        result = await db.execute(select(Product.category).distinct().where(Product.is_active == True))
        return [r[0] for r in result.fetchall()]

    @staticmethod
    async def get_count(db: AsyncSession) -> int:
        result = await db.execute(select(func.count()).where(Product.is_active == True).select_from(Product))
        return result.scalar()