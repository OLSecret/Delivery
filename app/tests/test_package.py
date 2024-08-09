import asyncio
import httpx
import pytest
from sqlalchemy import text, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models import  Package
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.database import DATABASE_URL
from app.main import app, on_startup

ASYNC_DATABASE_URL = DATABASE_URL.replace("pymysql", "asyncmy")
async_engine = create_async_engine(ASYNC_DATABASE_URL)

# Create an asynchronous session class
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# Define an async_session function for tests
async def async_session():
    async with AsyncSessionLocal() as session:
        yield session

@pytest.fixture(scope="module")
async def setup_database():
    try:
        await on_startup()
    except:
        pass

    return None

@pytest.fixture
async def app_client(setup_database):
    async with httpx.AsyncClient(app=app, base_url="http://test") as app_client:
        yield app_client


@pytest.fixture
async def add_packages_for_user():
    user_id = 164
    packages_to_add = [
        {"name": "Package 1", "type_id": 1, "user_id": 321, "weight": 10.5, "value": 100.0, "delivery_cost": 5.0},
        {"name": "Package 2", "type_id": 1, "user_id": user_id, "weight": 11.5, "value": 90.0, "delivery_cost": 5.0},
        {"name": "Package 3", "type_id": 1, "user_id": user_id, "weight": 12.5, "value": 80.0, "delivery_cost": 5.0},
        {"name": "Package 4", "type_id": 1, "user_id": user_id, "weight": 13.5, "value": 70.0, "delivery_cost": 5.0},
        {"name": "Package 5", "type_id": 2, "user_id": user_id, "weight": 14.5, "value": 60.0, "delivery_cost": 5.0},
        {"name": "Package 6", "type_id": 1, "user_id": user_id, "weight": 15.5, "value": 50.0, "delivery_cost": 5.0},
        {"name": "Package 7", "type_id": 2, "user_id": user_id, "weight": 16.5, "value": 40.0, "delivery_cost": 5.0},
        {"name": "Package 8", "type_id": 1, "user_id": user_id, "weight": 17.5, "value": 30.0, "delivery_cost": 5.0},
        {"name": "Package 9", "type_id": 2, "user_id": user_id, "weight": 18.5, "value": 20.0, "delivery_cost": 5.0},
    ]

    async_session_instance = AsyncSessionLocal()

    try:
        async with async_session_instance.begin():
            for package in packages_to_add:
                db_package = Package(**package)
                async_session_instance.add(db_package)
            await async_session_instance.commit()
        try:
            yield
        # Clean up the added packages
        finally:
            async with async_session_instance.begin():
                try:
                    await async_session_instance.execute(delete(Package).where(Package.user_id == user_id))
                    await async_session_instance.commit()
                except Exception as e:
                    await async_session_instance.rollback()
                    raise
    finally:
        await async_session_instance.close()


# Test function to check the database connection
@pytest.mark.asyncio
async def test_database_connection():
    engine = create_async_engine(ASYNC_DATABASE_URL, echo=True, future=True)

    async with engine.connect() as conn:
        result = await conn.execute(text("SHOW TABLES"))
        tables = result.fetchall()
        assert tables is not None

# Test function to verify package registration with a valid type_id
@pytest.mark.asyncio
async def test_register_package_valid_type(app_client):
    response = await app_client.post("/register", json={
        "name": "Valid Package",
        "weight": 2.5,
        "type_id": 1,
        "value": 100.0,
        "user_id": 164
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Valid Package"
    return response.json()["id"]

# Test function to verify the retrieval user's packages
@pytest.mark.asyncio
async def test_show_packages(app_client):
    user_id = 164

    # Make the POST request to the /show endpoint with the user_id
    response = await app_client.post("/show", json={
        "user_id": user_id,
        "offset": 456,
        "limit": 10,
    })
    assert response.status_code == 200
    #Get the JSON response data
    packages = response.json()

# Test function to verify the retrieval of all package types
@pytest.mark.asyncio
async def test_get_package_types(app_client):
    response = await app_client.get("/types")
    assert response.status_code == 200
    expected_data = [
        {"id": 1, "name": "clothing"},
        {"id": 2, "name": "electronics"},
        {"id": 3, "name": "miscellaneous"},
    ]
    assert response.json() == expected_data


# Test function to verify the retrieval of a package by its id
@pytest.mark.asyncio
async def test_get_package(app_client):
    package_id = await test_register_package_valid_type(app_client)
    # Make the GET request to the /package/{package_id} endpoint
    response = await app_client.get(f"/package/{package_id}")
    assert response.status_code == 200

    package = response.json()
    # Verify the package data
    expected_data = {'delivery_cost': None,
                     'id': package_id,
                     'name': 'Valid Package',
                     'type_id': 1,
                     'value': 100.0,
                     'weight': 2.5,
                     'user_id': 164,
                    }

    assert package == expected_data


@pytest.mark.asyncio
async def test_register_package_invalid_type(app_client):
    response = await app_client.post("/register", json={
        "name": "Invalid Package",
        "weight": 2.5,
        "type_id": 999,  # invalid type_id
        "value": 100.0,
        "user_id": 164
    })
    assert response.status_code == 422  # Unprocessable Entity
    assert response.json()["detail"][0]["msg"] == "Value error, Invalid type_id" # !!!!!!!!!!!!! XXXXXXXXXXXXXXX!!!!!!


@pytest.mark.asyncio
async def test_register_package_invalid_weight(app_client):
    response = await app_client.post("/register", json={
        "name": "Invalid Package",
        "weight": -1.0,  # invalid weight
        "type_id": 1,
        "value": 100.0,
        "user_id": 164
    })
    assert response.status_code == 422  # Unprocessable Entity
    assert response.json()["detail"][0]["msg"] == "Value error, Weight must be non-negative"

@pytest.mark.asyncio
async def test_register_package_invalid_value(app_client):
    response = await app_client.post("/register", json={
        "name": "Invalid Package",
        "weight": 2.5,
        "type_id": 1,
        "value": -100.0,  # invalid value
        "user_id": 164
    })
    assert response.status_code == 422  # Unprocessable Entity
    assert response.json()["detail"][0]["msg"] == "Value error, Value must be non-negative"

@pytest.mark.asyncio
async def test_register_package_invalid_name(app_client):
    response = await app_client.post("/register", json={
        "name": "<script>alert('XSS')</script>",  # invalid name (XSS attempt)
        "weight": 2.5,
        "type_id": 1,
        "value": 100.0,
        "user_id": 164
    })
    assert response.status_code == 422  # Unprocessable Entity
    assert response.json()["detail"][0]["msg"] == "Value error, Invalid name"

# Tests function to verify the retrieval user's packages (different options)
@pytest.mark.asyncio
async def test_show_packages_no_package_type(app_client):
    user_id = 164
    offset = 0
    limit = 10

    # Make the POST request to the /show endpoint with the user_id
    response = await app_client.post("/show", json={
        "user_id": user_id,
        "offset": offset,
        "limit": limit,
    })
    assert response.status_code == 200
    packages = response.json()
    assert len(packages) > 0

@pytest.mark.asyncio
async def test_show_packages_with_package_type(app_client):
    user_id = 164
    package_type = 1
    offset = 0
    limit = 10

    # Make the POST request to the /show endpoint with the user_id and package_type
    response = await app_client.post("/show", json={
        "user_id": user_id,
        "package_type": package_type,
        "offset": offset,
        "limit": limit,
    })
    assert response.status_code == 200
    packages = response.json()
    for package in packages:
        assert package['type_id'] == package_type

@pytest.mark.asyncio
async def test_show_packages_no_packages(app_client):
    user_id = 999  # User ID with no packages
    offset = 0
    limit = 10

    # Make the POST request to the /show endpoint with the user_id
    response = await app_client.post("/show", json={
        "user_id": user_id,
        "offset": offset,
        "limit": limit,
    })
    assert response.status_code == 200
    packages = response.json()
    assert len(packages) == 0

@pytest.mark.asyncio
async def test_show_packages_offset_limit_few_packages(app_client):
    user_id = 124
    package_type = 1
    offset = 5
    limit = 3

    # Make the POST request to the /show endpoint with the user_id and package_type
    response = await app_client.post("/show", json={
        "user_id": user_id,
        "package_type": package_type,
        "offset": offset,
        "limit": limit,
    })

    assert response.status_code == 200
    packages = response.json()
    length = await get_real_limit(package_type, user_id)
    assert len(packages) == min(length, limit)
    for i, package in enumerate(packages):
        assert package.id == i + offset + 1


async def get_real_limit(package_type, user_id):
    engine = create_async_engine(ASYNC_DATABASE_URL, echo=True, future=True)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with engine.begin() as conn:
    #session = AsyncSessionLocal()
    #async with session.begin():
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Package).filter_by(user_id=user_id, type_id=package_type))
            packages = result.scalars().all()
            lenght = len(packages)
            session.close()
    return lenght


@pytest.mark.asyncio
async def test_show_packages_offset_limit_lots_packages(app_client, add_packages_for_user):
    user_id = 164
    package_type = 1
    offset = 2
    limit = 3

    # Make the POST request to the /show endpoint with the user_id and package_type
    response = await app_client.post("/show", json={
        "user_id": user_id,
        "package_type": package_type,
        "offset": offset,
        "limit": limit,
    })
    #await asyncio.wait([response])

    assert response.status_code == 200
    packages = response.json()
    length = await get_real_limit(package_type, user_id)
    # Assert that the length of the packages list is equal to the limit
    assert len(packages) == min(limit, length)

    # Assert that the packages are of the correct type
    for package in packages:
        assert package.get("type_id") == package_type

    # Assert that the packages are for the correct user
    for package in packages:
        assert package.get("user_id") == user_id


@pytest.mark.asyncio
async def test_get_package_not_found(app_client):
    package_id = 999  # does not exist in the database
    response = await app_client.get(f"/package/{package_id}")
    assert response.status_code == 404
    error_response = response.json()
    assert error_response["detail"] == "Package not found"

@pytest.mark.asyncio
async def test_get_package_invalid_id(app_client):
    package_id = "not_an_integer"  # invalid ID
    response = await app_client.get(f"/package/{package_id}")
    assert response.status_code == 422
    error_response = response.json()
    assert error_response["detail"][0]["msg"] == "Input should be a valid integer, unable to parse string as an integer"
