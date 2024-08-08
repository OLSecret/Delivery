import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from sqlalchemy import select
from app.main import app, update_delivery_costs, on_startup
from app.database import Base, DATABASE_URL
from app.models import Package, PackageType
import redis
import os

# Initialize TestClient
client = TestClient(app)

# Initialize Redis client for testing
redis_client = redis.Redis(host='redis', port=6379, db=0)

ASYNC_DATABASE_URL = DATABASE_URL.replace("pymysql", "asyncmy")


@pytest.fixture(scope="module")
async def setup_database():
    try:
        await on_startup()
    except:
        pass

    engine = create_async_engine(ASYNC_DATABASE_URL, echo=True, future=True)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with AsyncSessionLocal() as session:
        test_package = Package(name="Test Package", weight=2.0, type_id=1, value=100.0, user_id=1)
        session.add(test_package)

        await session.commit()
        await session.close()
    return None


@pytest.mark.asyncio
async def test_update_delivery_costs(setup_database):
    # Set exchange rate in Redis
    usd_to_rub = 73.00  # Example exchange rate
    redis_client.set("usd_to_rub", usd_to_rub)

    # Call the update_delivery_costs function explicitly
    await update_delivery_costs()

    engine = create_async_engine(ASYNC_DATABASE_URL, echo=True, future=True)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Package).filter_by(name="Test Package"))
            package = result.scalars().all()
            package = package[0]
            expected_cost = (package.weight * 0.5 + package.value * 0.01) * usd_to_rub
            assert package.delivery_cost == expected_cost
            session.close()
