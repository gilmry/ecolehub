from fastapi import FastAPI, Depends, HTTPException, Form, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
from typing import List, Optional
from uuid import UUID

# Import Stage 1 models and schemas
from .models_stage1 import Base, User, Child, SELService, SELTransaction, SELBalance, SELCategory
from .schemas_stage1 import (
    UserCreate, UserResponse, UserUpdate,
    ChildCreate, ChildResponse, ChildUpdate,
    SELServiceCreate, SELServiceResponse, SELServiceUpdate, SELServiceWithOwner,
    SELTransactionCreate, SELTransactionResponse, SELTransactionUpdate, SELTransactionWithDetails,
    SELBalanceResponse, SELCategoryResponse, SELDashboard,
    Token, TransactionStatus
)
from .sel_service import SELBusinessLogic

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ecolehub:ecolehub_secure_password@localhost:5432/ecolehub")
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production-very-important")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

# Database
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# FastAPI app
app = FastAPI(
    title="EcoleHub Stage 1 - SEL",
    version="1.0.0",
    description="Plateforme scolaire collaborative avec SEL - EcoleHub"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_sel_service(db: Session = Depends(get_db)):
    return SELBusinessLogic(db)

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )
    
    if credentials is None:
        raise credentials_exception
        
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# Root Endpoints
@app.get("/")
def read_root():
    return {
        "message": "EcoleHub API Stage 1 - SEL", 
        "status": "running",
        "école": "EcoleHub",
        "version": "1.0.0",
        "features": ["Authentication", "Profiles", "Children", "SEL System"]
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "Connected"
    except Exception as e:
        db_status = f"Error: {str(e)}"
    
    return {
        "status": "healthy", 
        "stage": 1,
        "database": "PostgreSQL",
        "database_status": db_status,
        "école": "EcoleHub"
    }

# Authentication Endpoints
@app.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db), sel_service: SELBusinessLogic = Depends(get_sel_service)):
    # Check if email already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")
    
    # Create user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create initial SEL balance
    sel_service.get_or_create_balance(db_user.id)
    
    # Create token
    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token)

@app.post("/login", response_model=Token)
def login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token)

# User Management
@app.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.put("/me", response_model=UserResponse)
def update_users_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user_update.first_name is not None:
        current_user.first_name = user_update.first_name
    if user_update.last_name is not None:
        current_user.last_name = user_update.last_name
    
    db.commit()
    db.refresh(current_user)
    return current_user

# Children Management
@app.get("/children", response_model=List[ChildResponse])
def get_children(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    children = db.query(Child).filter(Child.parent_id == current_user.id).all()
    return children

@app.post("/children", response_model=ChildResponse)
def create_child(
    child: ChildCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_child = Child(
        parent_id=current_user.id,
        first_name=child.first_name,
        class_name=child.class_name.value,
        birth_date=child.birth_date
    )
    db.add(db_child)
    db.commit()
    db.refresh(db_child)
    return db_child

@app.delete("/children/{child_id}")
def delete_child(
    child_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    child = db.query(Child).filter(
        Child.id == child_id, 
        Child.parent_id == current_user.id
    ).first()
    
    if not child:
        raise HTTPException(status_code=404, detail="Enfant non trouvé")
    
    db.delete(child)
    db.commit()
    return {"message": "Enfant supprimé"}

# SEL System Endpoints

# SEL Categories
@app.get("/sel/categories", response_model=List[SELCategoryResponse])
def get_sel_categories(sel_service: SELBusinessLogic = Depends(get_sel_service)):
    return sel_service.get_categories()

# SEL Balance
@app.get("/sel/balance", response_model=SELBalanceResponse)
def get_sel_balance(
    current_user: User = Depends(get_current_user), 
    sel_service: SELBusinessLogic = Depends(get_sel_service)
):
    balance = sel_service.get_or_create_balance(current_user.id)
    return balance

# SEL Services
@app.get("/sel/services", response_model=List[SELServiceWithOwner])
def get_sel_services(
    category: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    sel_service: SELBusinessLogic = Depends(get_sel_service)
):
    services = sel_service.get_available_services(current_user.id, category, limit)
    return [{"user": service.user, **service.__dict__} for service in services]

@app.get("/sel/services/mine", response_model=List[SELServiceResponse])
def get_my_sel_services(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    services = db.query(SELService).filter(SELService.user_id == current_user.id).all()
    return services

@app.post("/sel/services", response_model=SELServiceResponse)
def create_sel_service(
    service: SELServiceCreate,
    current_user: User = Depends(get_current_user),
    sel_service: SELBusinessLogic = Depends(get_sel_service)
):
    return sel_service.create_service(current_user.id, service)

@app.put("/sel/services/{service_id}", response_model=SELServiceResponse)
def update_sel_service(
    service_id: UUID,
    service_update: SELServiceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = db.query(SELService).filter(
        SELService.id == service_id,
        SELService.user_id == current_user.id
    ).first()
    
    if not service:
        raise HTTPException(status_code=404, detail="Service non trouvé")
    
    # Update fields
    if service_update.title is not None:
        service.title = service_update.title
    if service_update.description is not None:
        service.description = service_update.description
    if service_update.category is not None:
        service.category = service_update.category
    if service_update.units_per_hour is not None:
        service.units_per_hour = service_update.units_per_hour
    if service_update.is_active is not None:
        service.is_active = service_update.is_active
    
    db.commit()
    db.refresh(service)
    return service

# SEL Transactions
@app.get("/sel/transactions", response_model=List[SELTransactionWithDetails])
def get_sel_transactions(
    status: Optional[TransactionStatus] = Query(None),
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(SELTransaction).filter(
        (SELTransaction.from_user_id == current_user.id) | 
        (SELTransaction.to_user_id == current_user.id)
    )
    
    if status:
        query = query.filter(SELTransaction.status == status.value)
    
    transactions = query.order_by(SELTransaction.created_at.desc()).limit(limit).all()
    
    # Add related data
    result = []
    for transaction in transactions:
        result.append({
            **transaction.__dict__,
            "from_user": transaction.from_user,
            "to_user": transaction.to_user,
            "service": transaction.service
        })
    
    return result

@app.post("/sel/transactions", response_model=SELTransactionResponse)
def create_sel_transaction(
    transaction: SELTransactionCreate,
    current_user: User = Depends(get_current_user),
    sel_service: SELBusinessLogic = Depends(get_sel_service)
):
    return sel_service.create_transaction(current_user.id, transaction)

@app.put("/sel/transactions/{transaction_id}/approve", response_model=SELTransactionResponse)
def approve_sel_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    sel_service: SELBusinessLogic = Depends(get_sel_service)
):
    return sel_service.approve_transaction(transaction_id, current_user.id)

@app.put("/sel/transactions/{transaction_id}/cancel", response_model=SELTransactionResponse)
def cancel_sel_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    sel_service: SELBusinessLogic = Depends(get_sel_service)
):
    return sel_service.cancel_transaction(transaction_id, current_user.id)

# SEL Dashboard
@app.get("/sel/dashboard")
def get_sel_dashboard(
    current_user: User = Depends(get_current_user),
    sel_service: SELBusinessLogic = Depends(get_sel_service)
):
    return sel_service.get_user_dashboard(current_user.id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)