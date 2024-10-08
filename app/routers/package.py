import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import SessionLocal

# Create an APIRouter instance for organizing the endpoints
router = APIRouter()

# Dependency that provides a database session for each request
def get_db():
    """ Returns a database session for the current request. """
    db = SessionLocal()
    try:
        yield db  # Yield the database session to be used by the request
    finally:
        db.close()  # Ensure the session is closed after the request is finished


# Endpoint to register a new package
@router.post("/register", response_model=schemas.Package)
def register_package(package: schemas.PackageCreate, db: Session = Depends(get_db)):
    """ Registers a new package in the database. """
    # Validate if the provided type_id exists in the predefined package types
    if package.type_id not in models.PACKAGE_TYPES.values():
        raise HTTPException(status_code=400, detail="Invalid type_id")
    # Validate if the provided user_id is correct
    if package.user_id is None or package.user_id < 0:
        raise HTTPException(status_code=400, detail="Invalid user_id")
    # Create a new Package instance from the request data
    db_package = models.Package(**package.dict())
    db.add(db_package)
    db.commit()
    db.refresh(db_package)
    return db_package

# Endpoint to show user's packages
@router.post("/show", response_model=List[schemas.Package])
def show_packages(show_request: schemas.ShowPackagesRequest, db: Session = Depends(get_db)):
    """ Retrieves a list of packages based on the provided filter criteria. """
    packages = []
    if show_request.package_type > -1:
        packages = (db.query(models.Package)
                .filter(models.Package.user_id == show_request.user_id,
                         models.Package.type_id == show_request.package_type
                        )
                .offset(show_request.offset)
                .limit(show_request.limit)
                .all())
    else:
        packages = (db.query(models.Package)
                .filter(models.Package.user_id == show_request.user_id)
                .offset(show_request.offset)
                .limit(show_request.limit)
                .all())
    return packages

# Endpoint to retrieve all package types
@router.get("/types", response_model=List[schemas.PackageType])
def get_package_types(db: Session = Depends(get_db)):
    """ Retrieves a list of all available package types. """
    # Query the database for all PackageType entries
    return db.query(models.PackageType).all()


# Endpoint to retrieve data about a package by its id
@router.get("/package/{package_id}", response_model=schemas.Package)
def get_package(package_id: int, db: Session = Depends(get_db)):
    """ Retrieves a single package by its ID. """
    package = db.query(models.Package).filter(models.Package.id == package_id).first()
    if package is None:
        raise HTTPException(status_code=404, detail="Package not found")
    return package

