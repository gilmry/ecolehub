from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum

# Enums
class TransactionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class BelgianClass(str, Enum):
    M1 = "M1"
    M2 = "M2"
    M3 = "M3"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"
    P5 = "P5"
    P6 = "P6"

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)

class UserResponse(UserBase):
    id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Child Schemas
class ChildBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    class_name: BelgianClass
    birth_date: Optional[datetime] = None

class ChildCreate(ChildBase):
    pass

class ChildUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    class_name: Optional[BelgianClass] = None
    birth_date: Optional[datetime] = None

class ChildResponse(ChildBase):
    id: UUID
    parent_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# SEL Category Schemas
class SELCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)

class SELCategoryResponse(SELCategoryBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# SEL Service Schemas
class SELServiceBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: str = Field(..., min_length=1, max_length=50)
    units_per_hour: int = Field(default=60, ge=1, le=300)  # 1 to 5 hours max per service
    new_category_name: Optional[str] = Field(None, max_length=100)  # For custom categories

class SELServiceCreate(SELServiceBase):
    pass

class SELServiceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    units_per_hour: Optional[int] = Field(None, ge=1, le=300)
    is_active: Optional[bool] = None

class SELServiceResponse(SELServiceBase):
    id: UUID
    user_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# SEL Transaction Schemas
class SELTransactionBase(BaseModel):
    to_user_id: UUID
    service_id: Optional[UUID] = None
    units: int = Field(..., ge=1, le=600)  # Max 10 hours per transaction
    description: Optional[str] = None

class SELTransactionCreate(SELTransactionBase):
    @validator('units')
    def validate_units(cls, v):
        if v <= 0:
            raise ValueError('Units must be positive')
        if v > 600:  # 10 hours max
            raise ValueError('Maximum 600 units (10 hours) per transaction')
        return v

class SELTransactionUpdate(BaseModel):
    status: Optional[TransactionStatus] = None
    description: Optional[str] = None
    completed_at: Optional[datetime] = None

class SELTransactionResponse(SELTransactionBase):
    id: UUID
    from_user_id: UUID
    status: TransactionStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    updated_at: datetime
    
    class Config:
        from_attributes = True

# SEL Balance Schemas
class SELBalanceResponse(BaseModel):
    user_id: UUID
    balance: int
    total_given: int
    total_received: int
    updated_at: datetime
    
    # Computed fields
    @validator('balance')
    def validate_balance_limits(cls, v):
        if v < -300:
            raise ValueError('Balance cannot go below -300 units')
        if v > 600:
            raise ValueError('Balance cannot exceed 600 units')
        return v
    
    class Config:
        from_attributes = True

# Transaction with related data
class SELTransactionWithDetails(SELTransactionResponse):
    from_user: UserResponse
    to_user: UserResponse
    service: Optional[SELServiceResponse] = None
    
    class Config:
        from_attributes = True

# Service with owner details
class SELServiceWithOwner(SELServiceResponse):
    user: UserResponse
    
    class Config:
        from_attributes = True

# Dashboard summary
class SELDashboard(BaseModel):
    balance: SELBalanceResponse
    active_services: int
    pending_transactions: int
    recent_transactions: List[SELTransactionWithDetails]
    available_services: List[SELServiceWithOwner]

# Authentication
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None