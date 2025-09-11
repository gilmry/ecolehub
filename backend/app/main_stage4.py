"""
EcoleHub Stage 4 - Complete platform with Analytics + Multilingual
Final stage: 200+ families with monitoring and international support
"""

from fastapi import FastAPI, Depends, HTTPException, Form, Header, Query, WebSocket, WebSocketDisconnect, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import Response
from sqlalchemy import create_engine, text, desc, and_, or_, func
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from datetime import datetime, timedelta, date
from jose import JWTError, jwt
import os
import redis
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
import time

# Prometheus monitoring
from prometheus_fastapi_instrumentator import Instrumentator

# Import all models and services from previous stages
from .models_stage1 import Base, User, Child, SELService, SELTransaction, SELBalance, SELCategory
from .models_stage2 import Conversation, Message, ConversationParticipant, Event, EventParticipant, UserStatus
from .models_stage3 import ShopProduct, ShopInterest, ShopOrder, ShopOrderItem, EducationResource, ResourceAccess

# Import schemas and services
from .schemas_stage1 import *
from .sel_service import SELBusinessLogic
from .websocket_manager import websocket_manager
from .shop_service import ShopCollaborativeService
from .mollie_service import mollie_service
from .minio_service import minio_service
from .analytics_service import EcoleHubAnalytics, get_analytics_service

# Additional schemas for Stage 4
from pydantic import BaseModel

class MessageCreate(BaseModel):
    content: str

class AnalyticsRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    metric_type: Optional[str] = None

# Import secrets manager
from .secrets_manager import get_jwt_secret, get_database_url, get_redis_url, get_external_api_key, secrets_manager

# Configuration sécurisée
try:
    SECRET_KEY = get_jwt_secret()
    DATABASE_URL = get_database_url()
    REDIS_URL = get_redis_url()
except RuntimeError as e:
    # Fallback pour développement sans Docker secrets
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-fallback-change-in-production")
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ecolehub:ecolehub_secure_password@localhost:5432/ecolehub")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

# Database
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Redis
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# FastAPI app
app = FastAPI(
    title="EcoleHub Stage 4 - Complete Platform",
    version="4.0.0", 
    description="Plateforme scolaire collaborative multilingue avec analytics - EcoleHub"
)

# Prometheus instrumentation
instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=[".*admin.*", "/metrics"],
    env_var_name="ENABLE_METRICS",
    inprogress_name="ecolehub_requests_inprogress",
    inprogress_labels=True,
)

instrumentator.instrument(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:80",
        "http://127.0.0.1",
        "https://*.ngrok.io",  # Support ngrok domains
        "https://*.ngrok-free.app",  # New ngrok domains
        "https://*.ngrok.app",
        "*"  # Temporary for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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

def get_shop_service(db: Session = Depends(get_db)):
    return ShopCollaborativeService(db)

def get_redis():
    return redis_client

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

# Middleware for analytics tracking
@app.middleware("http")
async def track_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Track response time
    process_time = time.time() - start_time
    
    # Log to analytics if user is authenticated
    if hasattr(request.state, 'user'):
        analytics = get_analytics_service(next(get_db()), redis_client)
        analytics.track_user_action(
            str(request.state.user.id),
            f"api_call_{request.method}_{request.url.path}",
            {"response_time": process_time, "status_code": response.status_code}
        )
    
    return response

# ==========================================
# ROOT + HEALTH + METRICS ENDPOINTS
# ==========================================

@app.get("/")
def read_root():
    return {
        "message": "EcoleHub API Stage 4 - Complete Platform", 
        "status": "running",
        "école": "EcoleHub",
        "version": "4.0.0",
        "features": ["Authentication", "Profiles", "Children", "SEL System", "Messaging", "Events", "Shop", "Education", "Analytics", "Multilingual"],
        "languages": ["fr-BE", "nl-BE", "en"],
        "capacity": "200+ families"
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db), redis_conn = Depends(get_redis)):
    try:
        # Test database
        db.execute(text("SELECT 1"))
        db_status = "Connected"
    except Exception as e:
        db_status = f"Error: {str(e)}"
    
    try:
        # Test Redis
        redis_conn.ping()
        redis_status = "Connected"
    except Exception as e:
        redis_status = f"Error: {str(e)}"
    
    try:
        # Test MinIO
        minio_service.client.bucket_exists("test")
        minio_status = "Connected"
    except Exception as e:
        minio_status = f"Error: {str(e)}"
    
    return {
        "status": "healthy", 
        "stage": 4,
        "database": "PostgreSQL",
        "database_status": db_status,
        "redis": "Redis",
        "redis_status": redis_status,
        "minio": "MinIO",
        "minio_status": minio_status,
        "analytics": "Enabled",
        "multilingual": "FR-BE/NL-BE/EN",
        "école": "EcoleHub"
    }

@app.get("/metrics")
def get_metrics(db: Session = Depends(get_db), redis_conn = Depends(get_redis)):
    """Prometheus metrics endpoint for EcoleHub monitoring."""
    analytics = get_analytics_service(db, redis_conn)
    return Response(content=analytics.get_prometheus_metrics(), media_type="text/plain")

# ==========================================
# ANALYTICS ENDPOINTS (NEW STAGE 4)
# ==========================================

@app.get("/analytics/platform")
def get_platform_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    redis_conn = Depends(get_redis)
):
    """Get platform overview analytics (admin only)."""
    if 'admin' not in current_user.email and 'direction' not in current_user.email:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    analytics = get_analytics_service(db, redis_conn)
    return analytics.get_platform_overview()

@app.get("/analytics/shop")
def get_shop_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    redis_conn = Depends(get_redis)
):
    """Get shop analytics (admin only)."""
    if 'admin' not in current_user.email and 'direction' not in current_user.email:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    analytics = get_analytics_service(db, redis_conn)
    return analytics.get_shop_analytics()

@app.get("/analytics/sel")
def get_sel_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    redis_conn = Depends(get_redis)
):
    """Get SEL system analytics (admin only)."""
    if 'admin' not in current_user.email and 'direction' not in current_user.email:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    analytics = get_analytics_service(db, redis_conn)
    return analytics.get_sel_analytics()

@app.get("/analytics/user/{user_id}")
def get_user_analytics(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    redis_conn = Depends(get_redis)
):
    """Get analytics for specific user (admin or self only)."""
    # Allow user to see their own analytics or admin to see any
    if str(user_id) != str(current_user.id) and 'admin' not in current_user.email:
        raise HTTPException(status_code=403, detail="Access denied")
    
    analytics = get_analytics_service(db, redis_conn)
    return analytics.get_user_analytics(str(user_id))

# ==========================================
# MULTILINGUAL ENDPOINTS (NEW STAGE 4) 
# ==========================================

@app.get("/i18n/locales")
def get_supported_locales():
    """Get supported languages for EcoleHub."""
    return [
        {"code": "fr-BE", "name": "Français (Belgique)", "flag": "🇧🇪", "primary": True},
        {"code": "nl-BE", "name": "Nederlands (België)", "flag": "🇳🇱", "primary": False},
        {"code": "en", "name": "English", "flag": "🇬🇧", "primary": False}
    ]

@app.get("/i18n/translations/{locale}")
def get_translations(locale: str):
    """Get translations for specific locale."""
    try:
        import json
        with open(f"/app/frontend/locales/{locale}.json", "r", encoding="utf-8") as f:
            translations = json.load(f)
        return translations
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Locale not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# AUTHENTICATION WITH ANALYTICS TRACKING
# ==========================================

@app.post("/register", response_model=Token)
def register(
    user: UserCreate, 
    db: Session = Depends(get_db), 
    sel_service: SELBusinessLogic = Depends(get_sel_service),
    redis_conn = Depends(get_redis)
):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")
    
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
    
    # Create SEL balance and user status
    sel_service.get_or_create_balance(db_user.id)
    user_status = UserStatus(user_id=db_user.id)
    db.add(user_status)
    
    # Auto-subscribe to announcement conversation
    announcement_conv = db.query(Conversation).filter(Conversation.type == 'announcement').first()
    if announcement_conv:
        participant = ConversationParticipant(conversation_id=announcement_conv.id, user_id=db_user.id)
        db.add(participant)
    
    db.commit()
    
    # Track registration in analytics
    analytics = get_analytics_service(db, redis_conn)
    analytics.track_user_action(str(db_user.id), 'register', {
        "user_type": "admin" if "admin" in user.email else "parent"
    })
    
    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token)

@app.post("/login", response_model=Token)
def login(
    email: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db),
    redis_conn = Depends(get_redis)
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    # Track login in analytics
    analytics = get_analytics_service(db, redis_conn)
    analytics.track_user_action(str(user.id), 'login', {
        "user_type": "admin" if "admin" in email else "parent"
    })
    
    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token)

# ==========================================
# ALL PREVIOUS STAGE ENDPOINTS (INHERITED)
# ==========================================

# User Management
@app.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

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

# SEL System
@app.get("/sel/categories", response_model=List[SELCategoryResponse])
def get_sel_categories(sel_service: SELBusinessLogic = Depends(get_sel_service)):
    return sel_service.get_categories()

@app.get("/sel/balance", response_model=SELBalanceResponse)
def get_sel_balance(current_user: User = Depends(get_current_user), sel_service: SELBusinessLogic = Depends(get_sel_service)):
    return sel_service.get_or_create_balance(current_user.id)

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
def create_sel_service(service: SELServiceCreate, current_user: User = Depends(get_current_user), sel_service: SELBusinessLogic = Depends(get_sel_service)):
    return sel_service.create_service(current_user.id, service)

# Shop System (Stage 3)
@app.get("/shop/products")
def get_shop_products(
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    shop_service: ShopCollaborativeService = Depends(get_shop_service)
):
    products = shop_service.get_products(category=category)
    
    result = []
    for product in products:
        product_info = shop_service.get_product_with_interest_count(product.id)
        
        user_interest = db.query(ShopInterest).filter(
            and_(
                ShopInterest.product_id == product.id,
                ShopInterest.user_id == current_user.id
            )
        ).first()
        
        result.append({
            **product_info,
            "user_interest": {
                "has_interest": user_interest is not None,
                "quantity": user_interest.quantity if user_interest else 0,
                "notes": user_interest.notes if user_interest else None
            }
        })
    
    return result

@app.post("/shop/products")
def create_shop_product(
    product_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new shop product (admin only)."""
    if 'admin' not in current_user.email and 'direction' not in current_user.email:
        raise HTTPException(status_code=403, detail="Accès admin requis")
    
    new_product = ShopProduct(
        name=product_data['name'],
        description=product_data.get('description'),
        base_price=product_data['base_price'],
        category=product_data['category'],
        min_quantity=product_data.get('min_quantity', 10),
        created_by=current_user.id
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return {
        "id": str(new_product.id),
        "message": "Produit créé avec succès",
        "name": new_product.name,
        "price": float(new_product.base_price)
    }

# Events (Stage 2)
@app.get("/events")
def get_events(upcoming_only: bool = Query(False), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Event).filter(Event.is_active == True)
    
    if upcoming_only:
        query = query.filter(Event.start_date >= datetime.utcnow())
    
    events = query.order_by(Event.start_date).all()
    
    result = []
    for event in events:
        participant = db.query(EventParticipant).filter(
            EventParticipant.event_id == event.id,
            EventParticipant.user_id == current_user.id
        ).first()
        
        participants_count = db.query(EventParticipant).filter(
            EventParticipant.event_id == event.id,
            EventParticipant.status == 'registered'
        ).count()
        
        result.append({
            "id": str(event.id),
            "title": event.title,
            "description": event.description,
            "start_date": event.start_date.isoformat(),
            "end_date": event.end_date.isoformat() if event.end_date else None,
            "location": event.location,
            "event_type": event.event_type,
            "class_name": event.class_name,
            "max_participants": event.max_participants,
            "participants_count": participants_count,
            "registration_required": event.registration_required,
            "is_registered": participant is not None,
            "created_at": event.created_at.isoformat()
        })
    
    return result

# Expose Prometheus metrics
instrumentator.expose(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)