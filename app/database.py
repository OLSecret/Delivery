# Import necessary components from SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Retrieve the database URL from the environment variables
# This URL specifies the database connection details (such as type, user, password, host, and database name)
DATABASE_URL = os.getenv("DATABASE_URL")

# Create an SQLAlchemy engine instance
# The engine is responsible for managing connections to the database and executing SQL queries
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class using the sessionmaker function
# autocommit=False means the session does not automatically commit transactions (you need to call commit manually)
# autoflush=False means the session does not automatically flush changes to the database before executing queries
# bind=engine associates this session with the engine we created
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
