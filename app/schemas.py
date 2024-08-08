# JSON<->DB type wrappers
import html
import re
from pydantic import BaseModel, validator
from app.models import PACKAGE_TYPES
from typing import Optional

# Base schema for package data
class PackageBase(BaseModel):
    # Basic fields required for a package
    name: str  # Name of the package
    weight: float  # Weight of the package
    type_id: int  # ID of the package type
    value: float  # Value of the package
    user_id: int #user_id
# Schema used when creating a new package
class PackageCreate(PackageBase):
    # Inherits all fields from PackageBase
    @validator('type_id')
    def type_id_must_be_valid(cls, v):
        if v not in PACKAGE_TYPES.values():
            raise ValueError('Invalid type_id')
        return v

    @validator('name')
    def sanitize_name(cls, v):
        if re.search(r'<[^>]*>', v):
            raise ValueError('Invalid name')
        return html.escape(v)

    @validator('weight')
    def validate_weight(cls, v):
        if v < 0:
            raise ValueError('Weight must be non-negative')
        return v

    @validator('value')
    def validate_value(cls, v):
        if v < 0:
            raise ValueError('Value must be non-negative')
        return v

# Schema representing a package, including database-generated fields
class Package(PackageBase):
    # Additional field for the package ID
    id: int
    delivery_cost: Optional[float] = None
    # Configuration settings for the Pydantic model
    class Config:
        # Enables ORM mode for compatibility with SQLAlchemy models
        orm_mode = True

# Schema representing a package type
class PackageType(BaseModel):
    # Fields representing the package type
    id: int  # ID of the package type
    name: str  # Name of the package type

    # Configuration settings for the Pydantic model
    class Config:
        # Enables ORM mode for compatibility with SQLAlchemy models
        orm_mode = True

from enum import Enum
class PackageValueStatus(str, Enum):
    any = 'any'
    calculated = 'calculated'
    pending = 'pending'
class ShowPackagesRequest(BaseModel):
    user_id: int
    offset: int = 0
    limit: int = 20
    package_type: int = -1
    calculated_value: PackageValueStatus = PackageValueStatus.any

    @validator('package_type')
    def package_type_must_be_valid(cls, package_type):
        if package_type < -1:
            raise ValueError('Invalid package_type')
        return package_type

    @validator('limit')
    def limit_must_be_valid(cls, limit):
        if limit > 50 or limit < 1:
            raise ValueError('Invalid limit')
        return limit

    @validator('offset')
    def offset_must_be_valid(cls, offset):
        if offset < 0:
            raise ValueError('Invalid offset')
        return offset