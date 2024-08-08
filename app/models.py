# DB schema
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base, SessionLocal

# Define the database model for package types
class PackageType(Base):
    # Specify the name of the table in the database
    __tablename__ = "package_types"

    # Define the columns in the table
    id = Column(Integer, primary_key=True, index=True)  # Primary key, unique identifier
    name = Column(String(50), unique=True, index=True)  # Name of the package type, must be unique

# Define the database model for packages
class Package(Base):
    # Specify the name of the table in the database
    __tablename__ = "packages"

    # Define the columns in the table
    id = Column(Integer, primary_key=True, index=True)  # Primary key, unique identifier
    name = Column(String(100), index=True)  # Name of the package !!!! unique=True???
    weight = Column(Float)  # Weight of the package in some unit
    type_id = Column(Integer, ForeignKey("package_types.id"))  # Foreign key referencing PackageType
    value = Column(Float)  # Value of the package, e.g., in dollars
    delivery_cost = Column(Float, nullable=True)
    # Define the relationship with the PackageType model
    # This allows access to the related PackageType object via `package.type`
    type = relationship("PackageType")
    user_id = Column(Integer, index=True)

# Dictionary to map human-readable package type names to their corresponding IDs
PACKAGE_TYPES = {
    "clothing": 1,
    "electronics": 2,
    "miscellaneous": 3
}

def register_package_types():
    db = SessionLocal()
    try:
        for type_name, type_id in PACKAGE_TYPES.items():
            existing_type = db.query(PackageType).filter_by(id=type_id).first()
            if not existing_type:
                db.add(PackageType(id=type_id, name=type_name))
        db.commit()
    except Exception as e:
        db.rollback()  # Ensure the session is rolled back in case of an error
        print(f"Error registering package types: {e}")
    finally:
        db.close()

