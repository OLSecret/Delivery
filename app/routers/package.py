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
    db = SessionLocal()
    try:
        yield db  # Yield the database session to be used by the request
    finally:
        db.close()  # Ensure the session is closed after the request is finished


# Endpoint to register a new package
@router.post("/register", response_model=schemas.Package)
def register_package(package: schemas.PackageCreate, db: Session = Depends(get_db)):
    # Validate if the provided type_id exists in the predefined package types
    if package.type_id not in models.PACKAGE_TYPES.values():
        raise HTTPException(status_code=400, detail="Invalid type_id")

    # !!!!!!!!!!!!!!!!!!!!!! XXXXXXXX!!!!!
    if package.user_id is None or package.user_id < 0:
        raise HTTPException(status_code=400, detail="Invalid user_id")

    # Create a new Package instance from the request data
    db_package = models.Package(**package.dict()) #!!!!!!!!!!!!!!!!!!!!!! XXXXXXXX!!!!!
    db.add(db_package)  # Add the new package to the database session
    db.commit()  # Commit the transaction to save the package in the database
    db.refresh(db_package)  # Refresh the instance to get the updated data from the database
    return db_package  # Return the newly created package

#  !!!!
async def create_package(package: schemas.PackageCreate, db: Session):
    with db.begin(): #also possible to implement with 'locks'
        try:
            db_package = models.Package(**package.dict())
            db.add(db_package)
            db.commit()
            db.refresh(db_package)
            return db_package
        except SQLAlchemyError as e:
            logging.error(f"Error creating package: {e}")
            raise #HTTPException(status_code=400, detail=str(e))

@router.post("/register", response_model=schemas.Package)
async def register_package(package: schemas.PackageCreate, db: Session = Depends(get_db)):
    #if package.type_id not in models.PACKAGE_TYPES.values():
    #    raise HTTPException(status_code=400, detail="Invalid type_id")
    db_package = await create_package(package, db)
    return db_package

# !!!

# Endpoint to show user's packages
# почему нет " -> " после def ???
@router.post("/show", response_model=List[schemas.Package])
def show_packages(show_request: schemas.ShowPackagesRequest, db: Session = Depends(get_db)):
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
    # Query the database for all PackageType entries
    return db.query(models.PackageType).all()


# Endpoint to retrieve data about a package by its id
@router.get("/package/{package_id}", response_model=schemas.Package)
def get_package(package_id: int, db: Session = Depends(get_db)):
    # how to debug!!!!   ????
    #all_pckgs = db.query(models.Package).all()

    package = db.query(models.Package).filter(models.Package.id == package_id).first()
    if package is None:
        raise HTTPException(status_code=404, detail="Package not found")
    return package

