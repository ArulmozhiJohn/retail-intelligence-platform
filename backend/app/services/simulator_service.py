import asyncio
import random
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from loguru import logger

from app.db.database import AsyncSessionLocal
from app.models.store import Store
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.transaction import Transaction
from app.models.replenishment import Replenishment
from app.core.config import settings

fake = Faker()

# ── Static seed data ────────────────────────────────────────────────

REGIONS = ["North", "South", "East", "West", "Central", "Northeast"]

REGION_CITIES = {
    "North":     [("New Delhi","DL"),("Noida","UP"),("Gurgaon","HR"),("Chandigarh","PB"),("Lucknow","UP")],
    "South":     [("Chennai","TN"),("Bengaluru","KA"),("Hyderabad","TS"),("Kochi","KL"),("Coimbatore","TN")],
    "East":      [("Kolkata","WB"),("Bhubaneswar","OD"),("Patna","BR"),("Guwahati","AS"),("Ranchi","JH")],
    "West":      [("Mumbai","MH"),("Pune","MH"),("Ahmedabad","GJ"),("Surat","GJ"),("Nagpur","MH")],
    "Central":   [("Bhopal","MP"),("Indore","MP"),("Raipur","CG"),("Jabalpur","MP"),("Gwalior","MP")],
    "Northeast": [("Guwahati","AS"),("Shillong","ML"),("Agartala","TR"),("Imphal","MN"),("Aizawl","MZ")],
}

STORE_TYPES = ["standard", "standard", "standard", "flagship", "express"]

CATEGORIES = {
    "Electronics":     ["Smartphone","Laptop","Tablet","Headphones","Smartwatch","Charger","Speaker","Camera","Monitor","Keyboard"],
    "Groceries":       ["Organic Milk","Whole Wheat Bread","Free Range Eggs","Greek Yogurt","Cheddar Cheese","Butter","Orange Juice","Almond Milk","Pasta","Rice"],
    "Clothing":        ["T-Shirt","Jeans","Dress","Jacket","Sneakers","Hoodie","Shorts","Socks","Belt","Cap"],
    "Home & Garden":   ["Coffee Maker","Vacuum Cleaner","Air Purifier","Blender","Toaster","Lamp","Curtains","Pillow","Rug","Plant Pot"],
    "Health & Beauty": ["Shampoo","Conditioner","Face Wash","Moisturizer","Sunscreen","Toothpaste","Vitamins","Protein Powder","Lip Balm","Deodorant"],
    "Sports":          ["Yoga Mat","Dumbbell","Running Shoes","Water Bottle","Resistance Band","Jump Rope","Cycling Gloves","Tennis Racket","Football","Basketball"],
    "Toys":            ["LEGO Set","Action Figure","Board Game","Puzzle","Remote Car","Doll","Stuffed Animal","Card Game","Art Kit","Science Kit"],
    "Books":           ["Fiction Novel","Self-Help Book","Cookbook","Biography","Science Book","History Book","Children Book","Comic Book","Textbook","Travel Guide"],
    "Automotive":      ["Car Wax","Motor Oil","Air Freshener","Seat Cover","Phone Mount","Dash Cam","Jump Starter","Tire Gauge","Floor Mats","LED Bulbs"],
    "Office":          ["Notebook","Ballpoint Pens","Sticky Notes","Stapler","Scissors","Tape","Whiteboard","Desk Organizer","Mouse Pad","USB Hub"],
}

BRANDS = {
    "Electronics":     ["Samsung","Apple","Sony","LG","Bose","Logitech","Dell","HP","Canon","Anker"],
    "Groceries":       ["Organic Valley","Nature's Own","Happy Farms","Chobani","Tillamook","Kerrygold","Tropicana","Silk","Barilla","Lundberg"],
    "Clothing":        ["Nike","Levi's","Zara","North Face","Adidas","Champion","H&M","Calvin Klein","Tommy Hilfiger","Under Armour"],
    "Home & Garden":   ["Cuisinart","Dyson","Levoit","Ninja","Breville","IKEA","Eclipse","Beckham","nuLOOM","Costa Farms"],
    "Health & Beauty": ["Pantene","Tresemme","CeraVe","Neutrogena","Coppertone","Colgate","Nature Made","Optimum Nutrition","Burt's Bees","Dove"],
    "Sports":          ["Gaiam","Bowflex","Brooks","Hydro Flask","TheraBand","Crossrope","Pearl Izumi","Wilson","Spalding","Nike"],
    "Toys":            ["LEGO","Hasbro","Mattel","Ravensburger","Hot Wheels","Barbie","Ty","Bicycle","Crayola","Thames & Kosmos"],
    "Books":           ["Penguin","HarperCollins","Random House","Simon & Schuster","Hachette","Scholastic","Marvel","Wiley","Lonely Planet","DK"],
    "Automotive":      ["Meguiar's","Mobil","Little Trees","FH Group","iOttie","Vantrue","NOCO","Accutire","WeatherTech","Sylvania"],
    "Office":          ["Moleskine","BIC","Post-it","Swingline","Fiskars","Scotch","Quartet","Fellowes","SteelSeries","Anker"],
}

PRICE_RANGES = {
    "Electronics":     (29.99,  1299.99),
    "Groceries":       (1.99,   29.99),
    "Clothing":        (9.99,   199.99),
    "Home & Garden":   (14.99,  399.99),
    "Health & Beauty": (4.99,   79.99),
    "Sports":          (9.99,   299.99),
    "Toys":            (7.99,   149.99),
    "Books":           (6.99,   59.99),
    "Automotive":      (9.99,   199.99),
    "Office":          (2.99,   89.99),
}

PAYMENT_METHODS = ["credit_card","debit_card","cash","mobile_pay","gift_card"]


# ── SimulatorService ─────────────────────────────────────────────────

class SimulatorService:

    # ── Seeding ───────────────────────────────────────────────────────

    @staticmethod
    async def seed_all(db: AsyncSession) -> dict:
        store_count_res = await db.execute(select(func.count()).select_from(Store))
        if store_count_res.scalar() > 0:
            return {"message": "Database already seeded", "skipped": True}

        logger.info("Seeding database...")
        stores   = await SimulatorService._seed_stores(db)
        products = await SimulatorService._seed_products(db)
        await db.commit()

        inv_count = await SimulatorService._seed_inventory(db, stores, products)
        await db.commit()

        logger.info(f"Seeding complete: {len(stores)} stores, {len(products)} products, {inv_count} inventory records")
        return {
            "message": "Database seeded successfully",
            "stores":   len(stores),
            "products": len(products),
            "inventory_records": inv_count,
        }

    @staticmethod
    async def _seed_stores(db: AsyncSession) -> list:
        stores = []
        store_num = 1
        per_region = settings.NUM_STORES // len(REGIONS)

        for region, cities in REGION_CITIES.items():
            for i in range(per_region):
                city, state = random.choice(cities)
                store = Store(
                    id=str(uuid.uuid4()),
                    name=f"{city} {random.choice(['Central','Select','Metro','Mall','Hub','Bazaar','Square','Point'])} #{store_num:03d}",
                    code=f"STR{store_num:04d}",
                    region=region,
                    city=city,
                    state=state,
                    country="India",
                    latitude=round(random.uniform(8.0, 37.0), 6),
                    longitude=round(random.uniform(68.0, 97.0), 6),
                    store_type=random.choice(STORE_TYPES),
                    is_active=True,
                    opened_at=fake.date_time_between(start_date="-5y", end_date="-6m"),
                )
                db.add(store)
                stores.append(store)
                store_num += 1

        await db.flush()
        logger.info(f"Seeded {len(stores)} stores")
        return stores

    @staticmethod
    async def _seed_products(db: AsyncSession) -> list:
        products = []
        sku_num = 1
        per_category = settings.NUM_PRODUCTS // len(CATEGORIES)

        for category, item_names in CATEGORIES.items():
            brands     = BRANDS[category]
            price_min, price_max = PRICE_RANGES[category]

            for i in range(per_category):
                base_name  = random.choice(item_names)
                brand      = random.choice(brands)
                unit_price = round(random.uniform(price_min, price_max), 2)
                cost_price = round(unit_price * random.uniform(0.4, 0.7), 2)
                is_perishable = category == "Groceries"

                product = Product(
                    id=str(uuid.uuid4()),
                    name=f"{brand} {base_name} {fake.bothify('??-###').upper()}",
                    sku=f"SKU{sku_num:06d}",
                    barcode=fake.ean13(),
                    category=category,
                    subcategory=base_name,
                    brand=brand,
                    description=f"Premium {base_name} by {brand}. {fake.sentence()}",
                    unit_price=Decimal(str(unit_price)),
                    cost_price=Decimal(str(cost_price)),
                    unit_of_measure="each",
                    weight_kg=round(random.uniform(0.1, 10.0), 2),
                    is_active=True,
                    is_perishable=is_perishable,
                    shelf_life_days=random.randint(7, 365) if is_perishable else None,
                    reorder_point=random.randint(10, 30),
                    reorder_quantity=random.randint(50, 200),
                )
                db.add(product)
                products.append(product)
                sku_num += 1

        await db.flush()
        logger.info(f"Seeded {len(products)} products")
        return products

    @staticmethod
    async def _seed_inventory(db: AsyncSession, stores: list, products: list) -> int:
        count = 0
        # Each store carries ~60% of products
        for store in stores:
            store_products = random.sample(products, k=int(len(products) * 0.6))
            for product in store_products:
                max_level   = random.randint(200, 500)
                on_hand     = random.randint(0, max_level)
                reorder_pt  = product.reorder_point

                inventory = Inventory(
                    id=str(uuid.uuid4()),
                    store_id=store.id,
                    product_id=product.id,
                    quantity_on_hand=on_hand,
                    quantity_reserved=random.randint(0, min(5, on_hand)),
                    quantity_in_transit=random.randint(0, 20),
                    reorder_point=reorder_pt,
                    max_stock_level=max_level,
                    last_restocked_at=fake.date_time_between(start_date="-30d", end_date="now", tzinfo=timezone.utc),
                    last_sold_at=fake.date_time_between(start_date="-7d", end_date="now", tzinfo=timezone.utc),
                )
                db.add(inventory)
                count += 1

            # Flush every 5000 records to avoid memory issues
            if count % 5000 == 0:
                await db.flush()
                logger.info(f"  Inventory progress: {count} records...")

        await db.flush()
        logger.info(f"Seeded {count} inventory records")
        return count

    # ── Transaction cycle ─────────────────────────────────────────────

    @staticmethod
    async def run_transaction_cycle(db: AsyncSession) -> dict:
        """
        Generate a burst of realistic transactions across random stores.
        """
        # Pick random stores and their inventory
        stores_res = await db.execute(
            select(Store).where(Store.is_active == True).order_by(func.random()).limit(20)
        )
        stores = stores_res.scalars().all()

        if not stores:
            return {"message": "No stores found. Please seed first.", "transactions_created": 0}

        created = 0
        replenishments_triggered = 0

        for store in stores:
            # Get available inventory for this store
            inv_res = await db.execute(
                select(Inventory)
                .where(Inventory.store_id == store.id)
                .where(Inventory.quantity_on_hand > 0)
                .order_by(func.random())
                .limit(10)
            )
            inv_items = inv_res.scalars().all()

            for inv in inv_items:
                # Get product price
                prod_res = await db.execute(
                    select(Product).where(Product.id == inv.product_id)
                )
                product = prod_res.scalar_one_or_none()
                if not product:
                    continue

                # Random sale quantity (1-5 units)
                qty = random.randint(1, min(5, inv.quantity_on_hand))
                unit_price  = float(product.unit_price)
                discount    = round(random.uniform(0, unit_price * 0.1), 2) if random.random() < 0.2 else 0
                tax         = round((unit_price * qty - discount) * 0.08, 2)
                total       = round((unit_price * qty) - discount + tax, 2)

                transaction = Transaction(
                    id=str(uuid.uuid4()),
                    store_id=store.id,
                    product_id=product.id,
                    transaction_type="sale",
                    quantity=qty,
                    unit_price=Decimal(str(unit_price)),
                    total_amount=Decimal(str(total)),
                    discount_amount=Decimal(str(discount)),
                    tax_amount=Decimal(str(tax)),
                    payment_method=random.choice(PAYMENT_METHODS),
                    pos_terminal=f"POS-{random.randint(1,5):02d}",
                    transacted_at=datetime.now(timezone.utc),
                )
                db.add(transaction)

                # Deduct inventory
                inv.quantity_on_hand = max(0, inv.quantity_on_hand - qty)
                inv.last_sold_at = datetime.now(timezone.utc)
                created += 1

                # Auto-trigger replenishment if low
                if inv.quantity_on_hand <= inv.reorder_point:
                    existing_rep = await db.execute(
                        select(Replenishment).where(
                            Replenishment.store_id == store.id,
                            Replenishment.product_id == product.id,
                            Replenishment.status.in_(["pending", "approved", "shipped"]),
                        )
                    )
                    if not existing_rep.scalar_one_or_none():
                        priority = "critical" if inv.quantity_on_hand == 0 else "high"
                        rep = Replenishment(
                            id=str(uuid.uuid4()),
                            store_id=store.id,
                            product_id=product.id,
                            requested_quantity=product.reorder_quantity * settings.REORDER_MULTIPLIER,
                            priority=priority,
                            trigger_reason="auto_sale_trigger",
                            status="pending",
                        )
                        db.add(rep)
                        replenishments_triggered += 1

        await db.flush()

        return {
            "transactions_created": created,
            "replenishments_triggered": replenishments_triggered,
            "stores_processed": len(stores),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ── Standalone runner (for Docker simulator service) ─────────────────

async def run_simulator():
    logger.info("Simulator worker starting...")
    await asyncio.sleep(5)  # Wait for DB to be ready

    async with AsyncSessionLocal() as db:
        # Auto-seed if empty
        store_count = await db.execute(select(func.count()).select_from(Store))
        if store_count.scalar() == 0:
            logger.info("Database empty — auto-seeding...")
            result = await SimulatorService.seed_all(db)
            logger.info(f"Seed result: {result}")

    logger.info(f"Simulator running — {settings.TRANSACTIONS_PER_MINUTE} tx/min target")

    cycle_interval = 60.0 / max(1, settings.TRANSACTIONS_PER_MINUTE / 20)

    while True:
        try:
            async with AsyncSessionLocal() as db:
                result = await SimulatorService.run_transaction_cycle(db)
                await db.commit()
                logger.info(
                    f"Cycle complete | "
                    f"tx={result['transactions_created']} | "
                    f"replenishments={result['replenishments_triggered']} | "
                    f"stores={result['stores_processed']}"
                )
        except Exception as e:
            logger.error(f"Simulator cycle error: {e}")

        await asyncio.sleep(cycle_interval)


if __name__ == "__main__":
    asyncio.run(run_simulator())