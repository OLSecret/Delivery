#from fastapi import FastAPI, Depends
#from fastapi_scheduler import SchedulerAdmin
#from app import models, database
#from sqlalchemy.orm import Session
#import httpx
#import redis
#import os

# Initialize Redis client
#redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0)


# Function to fetch exchange rate and cache it in Redis
#async def fetch_exchange_rate():
#    async with httpx.AsyncClient() as client:
#        response = await client.get("https://www.cbr-xml-daily.ru/daily_json.js")
#        response_data = response.json()
#        usd_to_rub = response_data["Valute"]["USD"]["Value"]
#        redis_client.set("usd_to_rub", usd_to_rub)
#        return usd_to_rub


# Function to calculate delivery cost for packages without cost
#async def calculate_delivery_cost(db: Session = Depends(database.get_db)):
    # Fetch USD to RUB rate from Redis
    #usd_to_rub = redis_client.get("usd_to_rub")
    #if not usd_to_rub:
    #    usd_to_rub = await fetch_exchange_rate()
    #else:
    #    usd_to_rub = float(usd_to_rub)

    # Query for packages without delivery cost
    #packages = db.query(models.Package).filter(models.Package.delivery_cost.is_(None)).all()

    #for package in packages:
    #    delivery_cost = (package.weight * 0.5 + package.value * 0.01) * usd_to_rub
    #    package.delivery_cost = delivery_cost
    #    db.add(package)

    #db.commit()


# Function to initialize the scheduler
#def init_scheduler(app: FastAPI):
#    scheduler = SchedulerAdmin(app=app)
#    scheduler.add_job(calculate_delivery_cost, "interval", minutes=5)
#    app.state.scheduler = scheduler