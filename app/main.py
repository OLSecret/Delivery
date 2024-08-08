# Import the FastAPI class from the fastapi module
from fastapi import FastAPI
from app.database import Base, engine
from app.models import register_package_types
from app.routers import package
from fastapi_utils.tasks import repeat_every
import redis
import httpx
import json
from app import models, schemas, database, routers
from app.database import SessionLocal

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(docs_url="/documentation", redoc_url="/redoc")

redis_client = redis.Redis(host='redis', port=6379, db=0)

# Fetch and cache the exchange rate
async def fetch_exchange_rate():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://www.cbr-xml-daily.ru/daily_json.js")
        data = response.json()
        usd_to_rub = data['Valute']['USD']['Value']
        redis_client.set("usd_to_rub", usd_to_rub)
        return usd_to_rub

@app.on_event("startup")
def on_startup():
    # Create all tables in the database based on the above models
    Base.metadata.create_all(bind=engine)
    # Ensure all package types are registered in the database
    register_package_types()

# Update delivery costs every 5 mins
@app.on_event("startup")
@repeat_every(seconds=300)  # 5 minutes
async def update_delivery_costs():
    db = SessionLocal()
    try:
        usd_to_rub = redis_client.get("usd_to_rub")
        if usd_to_rub is None:
            usd_to_rub = await fetch_exchange_rate()
        else:
            usd_to_rub = float(usd_to_rub)

        packages = db.query(models.Package).filter(models.Package.delivery_cost.is_(None)).all()
        for package in packages:
            delivery_cost = (package.weight * 0.5 + package.value * 0.01) * usd_to_rub
            package.delivery_cost = delivery_cost
        db.commit()
    finally:
        db.close()

# Fetch exchange rate at startup
@app.on_event("startup")
async def startup_event():
    await fetch_exchange_rate()

# Include the router from the package module
# This registers the API endpoints defined in package.router with the main FastAPI application
app.include_router(package.router)
