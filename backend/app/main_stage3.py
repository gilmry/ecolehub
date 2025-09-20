"""
EcoleHub Stage 3 - Main application with Shop + Education
Extends Stage 2 with collaborative shopping and educational resources
"""

import os
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

import redis
from fastapi import Depends, FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# Additional schemas for Stage 3
from pydantic import BaseModel
from sqlalchemy import and_, create_engine, desc, func, or_, text
from sqlalchemy.orm import Session, sessionmaker

from .minio_service import minio_service

# Import all models (Stage 1 + Stage 2 + Stage 3)
from .models_stage1 import Base, Child, SELService, SELTransaction, User
from .models_stage2 import (
    Conversation,
    ConversationParticipant,
    Event,
    EventParticipant,
    Message,
    UserStatus,
)
from .models_stage3 import EducationResource, ShopInterest, ShopProduct
from .mollie_service import mollie_service

# Import schemas and services
from .schemas_stage1 import (
    ChildCreate,
    ChildResponse,
    SELBalanceResponse,
    SELCategoryResponse,
    SELServiceCreate,
    SELServiceResponse,
    SELServiceWithOwner,
    SELTransactionCreate,
    SELTransactionResponse,
    SELTransactionWithDetails,
    Token,
    TransactionStatus,
    UserCreate,
    UserResponse,
)
from .sel_service import SELBusinessLogic
from .shop_service import ShopCollaborativeService


class MessageCreate(BaseModel):
    content: str


class ShopInterestCreate(BaseModel):
    quantity: int
    notes: Optional[str] = None


class EducationResourceCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    class_name: Optional[str] = None
    is_public: bool = False


# Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://ecolehub:ecolehub_secure_password@localhost:5432/ecolehub",
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production-very-important")
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
    title="EcoleHub Stage 3 - Boutique + Éducation",
    version="3.0.0",
    description="Plateforme scolaire collaborative avec boutique et éducation - EcoleHub",
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


def get_shop_service(db: Session = Depends(get_db)):
    return ShopCollaborativeService(db)


def get_redis():
    return redis_client


# Helper functions (same as previous stages)
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
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials"
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


# ==========================================
# ROOT + HEALTH ENDPOINTS
# ==========================================


@app.get("/")
def read_root():
    return {
        "message": "EcoleHub API Stage 3 - Boutique + Éducation",
        "status": "running",
        "école": "EcoleHub",
        "version": "3.0.0",
        "features": [
            "Authentication",
            "Profiles",
            "Children",
            "SEL System",
            "Messaging",
            "Events",
            "Shop",
            "Education",
        ],
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db), redis_conn=Depends(get_redis)):
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
        "stage": 3,
        "database": "PostgreSQL",
        "database_status": db_status,
        "redis": "Redis",
        "redis_status": redis_status,
        "minio": "MinIO",
        "minio_status": minio_status,
        "école": "EcoleHub",
    }


# ==========================================
# AUTHENTICATION (inherited from previous stages)
# ==========================================


@app.post("/register", response_model=Token)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
    sel_service: SELBusinessLogic = Depends(get_sel_service),
):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")

    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create SEL balance and user status
    sel_service.get_or_create_balance(db_user.id)
    user_status = UserStatus(user_id=db_user.id)
    db.add(user_status)

    # Auto-subscribe to announcement conversation
    announcement_conv = (
        db.query(Conversation).filter(Conversation.type == "announcement").first()
    )
    if announcement_conv:
        participant = ConversationParticipant(
            conversation_id=announcement_conv.id, user_id=db_user.id
        )
        db.add(participant)

    db.commit()

    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token)


@app.post("/login", response_model=Token)
def login(
    email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token)


# ==========================================
# USER & CHILDREN MANAGEMENT (inherited)
# ==========================================


@app.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/children", response_model=List[ChildResponse])
def get_children(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    children = db.query(Child).filter(Child.parent_id == current_user.id).all()
    return children


@app.post("/children", response_model=ChildResponse)
def create_child(
    child: ChildCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_child = Child(
        parent_id=current_user.id,
        first_name=child.first_name,
        class_name=child.class_name.value,
        birth_date=child.birth_date,
    )
    db.add(db_child)
    db.commit()
    db.refresh(db_child)

    # Auto-join class conversation
    class_conv = (
        db.query(Conversation)
        .filter(
            and_(
                Conversation.type == "class",
                Conversation.class_name == child.class_name.value,
            )
        )
        .first()
    )

    if class_conv:
        existing = (
            db.query(ConversationParticipant)
            .filter(
                ConversationParticipant.conversation_id == class_conv.id,
                ConversationParticipant.user_id == current_user.id,
            )
            .first()
        )

        if not existing:
            participant = ConversationParticipant(
                conversation_id=class_conv.id, user_id=current_user.id
            )
            db.add(participant)
            db.commit()

    return db_child


# ==========================================
# SEL SYSTEM (inherited from Stage 1)
# ==========================================


@app.get("/sel/categories", response_model=List[SELCategoryResponse])
def get_sel_categories(sel_service: SELBusinessLogic = Depends(get_sel_service)):
    return sel_service.get_categories()


@app.get("/sel/balance", response_model=SELBalanceResponse)
def get_sel_balance(
    current_user: User = Depends(get_current_user),
    sel_service: SELBusinessLogic = Depends(get_sel_service),
):
    return sel_service.get_or_create_balance(current_user.id)


@app.get("/sel/services", response_model=List[SELServiceWithOwner])
def get_sel_services(
    category: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    sel_service: SELBusinessLogic = Depends(get_sel_service),
):
    services = sel_service.get_available_services(current_user.id, category, limit)
    return [{"user": service.user, **service.__dict__} for service in services]


@app.get("/sel/services/mine", response_model=List[SELServiceResponse])
def get_my_sel_services(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    services = db.query(SELService).filter(SELService.user_id == current_user.id).all()
    return services


@app.post("/sel/services", response_model=SELServiceResponse)
def create_sel_service(
    service: SELServiceCreate,
    current_user: User = Depends(get_current_user),
    sel_service: SELBusinessLogic = Depends(get_sel_service),
):
    return sel_service.create_service(current_user.id, service)


@app.get("/sel/transactions", response_model=List[SELTransactionWithDetails])
def get_sel_transactions(
    status: Optional[TransactionStatus] = Query(None),
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(SELTransaction).filter(
        (SELTransaction.from_user_id == current_user.id)
        | (SELTransaction.to_user_id == current_user.id)
    )

    if status:
        query = query.filter(SELTransaction.status == status.value)

    transactions = query.order_by(SELTransaction.created_at.desc()).limit(limit).all()

    result = []
    for transaction in transactions:
        result.append(
            {
                **transaction.__dict__,
                "from_user": transaction.from_user,
                "to_user": transaction.to_user,
                "service": transaction.service,
            }
        )

    return result


@app.post("/sel/transactions", response_model=SELTransactionResponse)
def create_sel_transaction(
    transaction: SELTransactionCreate,
    current_user: User = Depends(get_current_user),
    sel_service: SELBusinessLogic = Depends(get_sel_service),
):
    return sel_service.create_transaction(current_user.id, transaction)


@app.put(
    "/sel/transactions/{transaction_id}/approve", response_model=SELTransactionResponse
)
def approve_sel_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    sel_service: SELBusinessLogic = Depends(get_sel_service),
):
    return sel_service.approve_transaction(transaction_id, current_user.id)


@app.put(
    "/sel/transactions/{transaction_id}/cancel", response_model=SELTransactionResponse
)
def cancel_sel_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    sel_service: SELBusinessLogic = Depends(get_sel_service),
):
    return sel_service.cancel_transaction(transaction_id, current_user.id)


# ==========================================
# MESSAGING SYSTEM (inherited from Stage 2)
# ==========================================


@app.post("/conversations/direct")
def create_direct_conversation(
    other_user_id: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create or get existing direct conversation between two users."""
    try:
        other_user_uuid = UUID(other_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID utilisateur invalide")

    # Check if conversation already exists
    existing = (
        db.query(Conversation)
        .join(ConversationParticipant)
        .filter(
            and_(
                Conversation.type == "direct",
                ConversationParticipant.user_id.in_([current_user.id, other_user_uuid]),
            )
        )
        .group_by(Conversation.id)
        .having(func.count(ConversationParticipant.user_id) == 2)
        .first()
    )

    if existing:
        return {
            "conversation_id": str(existing.id),
            "message": "Conversation existante",
        }

    # Get other user info
    other_user = db.query(User).filter(User.id == other_user_uuid).first()
    if not other_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # Create new conversation
    conversation = Conversation(
        name=f"{current_user.first_name} & {other_user.first_name}",
        type="direct",
        created_by=current_user.id,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    # Add participants
    participants = [
        ConversationParticipant(
            conversation_id=conversation.id, user_id=current_user.id
        ),
        ConversationParticipant(
            conversation_id=conversation.id, user_id=other_user_uuid
        ),
    ]

    for participant in participants:
        db.add(participant)

    db.commit()

    return {"conversation_id": str(conversation.id), "message": "Conversation créée"}


@app.get("/users/list")
def get_users_list(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get list of users for direct messaging (excluding current user)."""
    users = (
        db.query(User).filter(and_(User.id != current_user.id, User.is_active)).all()
    )

    return [
        {
            "id": str(user.id),
            "name": f"{user.first_name} {user.last_name}",
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        for user in users
    ]


@app.get("/conversations/{conversation_id}/messages")
def get_conversation_messages(
    conversation_id: UUID,
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get messages from a conversation."""
    participant = (
        db.query(ConversationParticipant)
        .filter(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == current_user.id,
        )
        .first()
    )

    if not participant:
        raise HTTPException(
            status_code=403, detail="Accès interdit à cette conversation"
        )

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(desc(Message.created_at))
        .limit(limit)
        .all()
    )

    messages.reverse()  # Oldest first

    return [
        {
            "id": str(msg.id),
            "conversation_id": str(msg.conversation_id),
            "user_id": str(msg.user_id),
            "user_name": f"{msg.user.first_name} {msg.user.last_name}",
            "content": msg.content,
            "message_type": msg.message_type,
            "created_at": msg.created_at.isoformat(),
            "edited_at": msg.edited_at.isoformat() if msg.edited_at else None,
        }
        for msg in messages
    ]


@app.post("/conversations/{conversation_id}/messages")
def send_message_to_conversation(
    conversation_id: UUID,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a message to a conversation."""
    participant = (
        db.query(ConversationParticipant)
        .filter(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == current_user.id,
        )
        .first()
    )

    if not participant:
        raise HTTPException(
            status_code=403, detail="Accès interdit à cette conversation"
        )

    message = Message(
        conversation_id=conversation_id,
        user_id=current_user.id,
        content=message_data.content.strip(),
        message_type="text",
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return {
        "id": str(message.id),
        "message": "Message envoyé",
        "created_at": message.created_at.isoformat(),
    }


@app.get("/conversations")
def get_conversations(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    participations = (
        db.query(ConversationParticipant)
        .filter(ConversationParticipant.user_id == current_user.id)
        .all()
    )

    conversations = []
    for participation in participations:
        conversation = participation.conversation
        last_message = (
            db.query(Message)
            .filter(Message.conversation_id == conversation.id)
            .order_by(desc(Message.created_at))
            .first()
        )

        conversations.append(
            {
                "id": str(conversation.id),
                "name": conversation.name,
                "type": conversation.type,
                "class_name": conversation.class_name,
                "last_message": {
                    "content": last_message.content if last_message else None,
                    "created_at": last_message.created_at.isoformat()
                    if last_message
                    else None,
                    "user_name": f"{last_message.user.first_name} {last_message.user.last_name}"
                    if last_message
                    else None,
                }
                if last_message
                else None,
                "updated_at": conversation.updated_at.isoformat(),
            }
        )

    return conversations


@app.get("/events")
def get_events(
    upcoming_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Event).filter(Event.is_active)

    if upcoming_only:
        query = query.filter(Event.start_date >= datetime.utcnow())

    events = query.order_by(Event.start_date).all()

    result = []
    for event in events:
        participant = (
            db.query(EventParticipant)
            .filter(
                EventParticipant.event_id == event.id,
                EventParticipant.user_id == current_user.id,
            )
            .first()
        )

        participants_count = (
            db.query(EventParticipant)
            .filter(
                EventParticipant.event_id == event.id,
                EventParticipant.status == "registered",
            )
            .count()
        )

        result.append(
            {
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
                "created_at": event.created_at.isoformat(),
            }
        )

    return result


# ==========================================
# NEW STAGE 3: SHOP ENDPOINTS
# ==========================================


@app.get("/shop/products")
def get_shop_products(
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    shop_service: ShopCollaborativeService = Depends(get_shop_service),
):
    """Get shop products for EcoleHub."""
    products = shop_service.get_products(category=category)

    result = []
    for product in products:
        product_info = shop_service.get_product_with_interest_count(product.id)

        # Check if current user has expressed interest
        user_interest = (
            db.query(ShopInterest)
            .filter(
                and_(
                    ShopInterest.product_id == product.id,
                    ShopInterest.user_id == current_user.id,
                )
            )
            .first()
        )

        result.append(
            {
                **product_info,
                "user_interest": {
                    "has_interest": user_interest is not None,
                    "quantity": user_interest.quantity if user_interest else 0,
                    "notes": user_interest.notes if user_interest else None,
                },
            }
        )

    return result


@app.post("/shop/products/{product_id}/interest")
def express_product_interest(
    product_id: UUID,
    interest: ShopInterestCreate,
    current_user: User = Depends(get_current_user),
    shop_service: ShopCollaborativeService = Depends(get_shop_service),
):
    """Express interest in a product for group buying."""
    return shop_service.express_interest(
        user_id=current_user.id,
        product_id=product_id,
        quantity=interest.quantity,
        notes=interest.notes,
    )


@app.delete("/shop/products/{product_id}/interest")
def cancel_product_interest(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    shop_service: ShopCollaborativeService = Depends(get_shop_service),
):
    """Cancel interest in a product."""
    return shop_service.cancel_interest(current_user.id, product_id)


@app.post("/shop/products")
def create_shop_product(
    product_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new shop product (admin only)."""
    # Simple admin check (can be improved)
    if "admin" not in current_user.email and "direction" not in current_user.email:
        raise HTTPException(status_code=403, detail="Accès admin requis")

    # Create product
    new_product = ShopProduct(
        name=product_data["name"],
        description=product_data.get("description"),
        base_price=product_data["base_price"],
        category=product_data["category"],
        min_quantity=product_data.get("min_quantity", 10),
        created_by=current_user.id,
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {
        "id": str(new_product.id),
        "message": "Produit créé avec succès",
        "name": new_product.name,
        "price": float(new_product.base_price),
    }


@app.put("/shop/products/{product_id}")
def update_shop_product(
    product_id: UUID,
    update_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update shop product (admin only)."""
    # Simple admin check
    if "admin" not in current_user.email and "direction" not in current_user.email:
        raise HTTPException(status_code=403, detail="Accès admin requis")

    product = db.query(ShopProduct).filter(ShopProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")

    # Update fields
    if "name" in update_data:
        product.name = update_data["name"]
    if "description" in update_data:
        product.description = update_data["description"]
    if "base_price" in update_data:
        product.base_price = update_data["base_price"]
    if "category" in update_data:
        product.category = update_data["category"]
    if "min_quantity" in update_data:
        product.min_quantity = update_data["min_quantity"]
    if "is_active" in update_data:
        product.is_active = update_data["is_active"]

    db.commit()
    db.refresh(product)

    return {
        "id": str(product.id),
        "message": "Produit mis à jour",
        "name": product.name,
        "is_active": product.is_active,
    }


@app.get("/shop/categories")
def get_shop_categories(
    shop_service: ShopCollaborativeService = Depends(get_shop_service),
):
    """Get available shop categories."""
    return shop_service.get_product_categories()


@app.get("/shop/orders/mine")
def get_my_shop_orders(
    current_user: User = Depends(get_current_user),
    shop_service: ShopCollaborativeService = Depends(get_shop_service),
):
    """Get user's shop order history."""
    return shop_service.get_user_orders(current_user.id)


@app.post("/shop/products/{product_id}/order")
def create_group_order(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    shop_service: ShopCollaborativeService = Depends(get_shop_service),
):
    """Create group order when threshold is met (admin only for now)."""
    return shop_service.create_group_order(product_id, current_user.id)


# ==========================================
# NEW STAGE 3: EDUCATION ENDPOINTS
# ==========================================


@app.get("/education/resources")
def get_education_resources(
    category: Optional[str] = Query(None),
    class_name: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get educational resources for EcoleHub."""
    query = db.query(EducationResource).filter(
        or_(
            EducationResource.is_public,
            EducationResource.created_by == current_user.id,
        )
    )

    if category:
        query = query.filter(EducationResource.category == category)

    if class_name:
        query = query.filter(EducationResource.class_name == class_name)

    resources = query.order_by(desc(EducationResource.created_at)).all()

    result = []
    for resource in resources:
        result.append(
            {
                "id": str(resource.id),
                "title": resource.title,
                "description": resource.description,
                "category": resource.category,
                "class_name": resource.class_name,
                "file_url": resource.file_url,
                "file_type": resource.file_type,
                "file_size": resource.file_size,
                "is_public": resource.is_public,
                "created_at": resource.created_at.isoformat(),
                "creator_name": f"{resource.creator.first_name} {resource.creator.last_name}"
                if resource.creator
                else "École",
            }
        )

    return result


@app.post("/education/resources")
def create_education_resource(
    resource: EducationResourceCreate,
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create educational resource (with optional file upload)."""
    file_url = None
    file_type = None
    file_size = None

    # Handle file upload if provided
    if file:
        upload_result = minio_service.upload_file(
            file.file,
            file.filename,
            bucket_type="education",
            content_type=file.content_type,
        )

        if not upload_result["success"]:
            raise HTTPException(status_code=400, detail=upload_result["error"])

        file_url = upload_result["file_url"]
        file_type = upload_result["content_type"]
        file_size = upload_result["size"]

    # Create resource
    db_resource = EducationResource(
        title=resource.title,
        description=resource.description,
        category=resource.category,
        class_name=resource.class_name,
        file_url=file_url,
        file_type=file_type,
        file_size=file_size,
        is_public=resource.is_public,
        created_by=current_user.id,
    )

    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)

    return {
        "id": str(db_resource.id),
        "message": "Ressource éducative créée",
        "file_uploaded": file is not None,
    }


@app.get("/education/categories")
def get_education_categories():
    """Get education resource categories."""
    return [
        {"id": "homework", "name": "Devoirs", "icon": "📝"},
        {"id": "calendar", "name": "Calendrier", "icon": "📅"},
        {"id": "forms", "name": "Formulaires", "icon": "📋"},
        {"id": "announcements", "name": "Annonces", "icon": "📢"},
        {"id": "resources", "name": "Ressources", "icon": "📚"},
    ]


# ==========================================
# PAYMENT ENDPOINTS (Belgian Mollie)
# ==========================================


@app.post("/payments/create")
def create_payment(
    amount: float = Form(...),
    description: str = Form(...),
    order_id: str = Form(...),
    current_user: User = Depends(get_current_user),
):
    """Create Mollie payment for EcoleHub orders."""
    redirect_url = f"http://localhost/payment/return/{order_id}"
    webhook_url = f"http://localhost:8000/payments/webhook"

    result = mollie_service.create_payment(
        amount=amount,
        description=description,
        user_email=current_user.email,
        order_id=order_id,
        redirect_url=redirect_url,
        webhook_url=webhook_url,
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@app.get("/payments/{payment_id}/status")
def get_payment_status(payment_id: str, current_user: User = Depends(get_current_user)):
    """Get payment status."""
    result = mollie_service.get_payment_status(payment_id)

    if not result["success"]:
        raise HTTPException(status_code=404, detail="Paiement non trouvé")

    return result


@app.post("/payments/webhook")
def mollie_webhook(payment_id: str = Form(...)):
    """Handle Mollie webhook for payment updates."""
    result = mollie_service.handle_webhook(payment_id)

    if result["success"]:
        # TODO: Update order status in database
        # TODO: Send notification to parents
        pass

    return {"status": "received"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
