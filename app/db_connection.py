from sqlalchemy.engine import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Create the engine with retry options
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Enable logging
    execution_options={
        "isolation_level": "REPEATABLE READ"
    },
    retry=True,  # Enable retry mechanism
    retry_interval=1,  # Retry interval in seconds
    max_retries=3  # Maximum number of retries
)

# Create a session maker with the engine
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Create a base class for declarative class definitions
# This Base class is used to define all the ORM models (i.e., the tables and their structure)
Base = declarative_base()

# Define a dependency that can be used to provide a database session to routes in the FastAPI application
# The function get_db will yield a database session (db) and then ensure it is properly closed
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()