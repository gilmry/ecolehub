"""
EcoleHub Stage 2 - Main application with Messaging and Events
Extends Stage 1 with real-time features
"""

from fastapi import FastAPI, Depends, HTTPException, Form, Header, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, text, desc, and_, or_, func
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
import redis
from typing import List, Optional
from uuid import UUID

# Import all models (Stage 1 + Stage 2)
from .models_stage1 import Base, User, Child, SELService, SELTransaction, SELBalance, SELCategory
from .models_stage2 import Conversation, Message, ConversationParticipant, Event, EventParticipant, UserStatus

# Import Stage 1 schemas and add Stage 2
from .schemas_stage1 import (
    UserCreate, UserResponse, UserUpdate,
    ChildCreate, ChildResponse, ChildUpdate, 
    SELServiceCreate, SELServiceResponse, SELServiceUpdate, SELServiceWithOwner,
    SELTransactionCreate, SELTransactionResponse, SELTransactionUpdate, SELTransactionWithDetails,
    SELBalanceResponse, SELCategoryResponse, SELDashboard,
    Token, TransactionStatus
)

from .sel_service import SELBusinessLogic
from .websocket_manager import websocket_manager

# Additional schemas for Stage 2
from pydantic import BaseModel

class MessageCreate(BaseModel):
    content: str

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ecolehub:ecolehub_secure_password@localhost:5432/ecolehub")
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
    title="EcoleHub Stage 2 - Messaging + Events",
    version="2.0.0", 
    description="Plateforme scolaire collaborative avec messagerie temps réel - EcoleHub"
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

def get_redis():
    return redis_client

# Helper functions (same as Stage 1)
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

# ==========================================
# ROOT + HEALTH ENDPOINTS
# ==========================================

@app.get("/")
def read_root():
    return {
        "message": "EcoleHub API Stage 2 - Messaging + Events", 
        "status": "running",
        "école": "EcoleHub",
        "version": "2.0.0",
        "features": ["Authentication", "Profiles", "Children", "SEL System", "Messaging", "Events", "Real-time"]
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
    
    return {
        "status": "healthy", 
        "stage": 2,
        "database": "PostgreSQL",
        "database_status": db_status,
        "redis": "Redis",
        "redis_status": redis_status,
        "école": "EcoleHub"
    }

# ==========================================
# AUTHENTICATION ENDPOINTS (from Stage 1)
# ==========================================

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
    
    # Create user status for messaging
    user_status = UserStatus(user_id=db_user.id)
    db.add(user_status)
    
    # Auto-join class conversations if user has children
    db.commit()  # Commit user first
    db.refresh(db_user)
    
    # Auto-subscribe to announcement conversation
    announcement_conv = db.query(Conversation).filter(
        Conversation.type == 'announcement'
    ).first()
    
    if announcement_conv:
        # Add user to announcement conversation
        existing_participant = db.query(ConversationParticipant).filter(
            ConversationParticipant.conversation_id == announcement_conv.id,
            ConversationParticipant.user_id == db_user.id
        ).first()
        
        if not existing_participant:
            participant = ConversationParticipant(
                conversation_id=announcement_conv.id,
                user_id=db_user.id
            )
            db.add(participant)
    
    db.commit()
    
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

# ==========================================
# USER MANAGEMENT (from Stage 1)
# ==========================================

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

# ==========================================
# CHILDREN MANAGEMENT (from Stage 1)
# ==========================================

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
    
    # Auto-join class conversation for this child's class
    class_conv = db.query(Conversation).filter(
        and_(
            Conversation.type == 'class',
            Conversation.class_name == child.class_name.value
        )
    ).first()
    
    if class_conv:
        # Check if already participant
        existing = db.query(ConversationParticipant).filter(
            ConversationParticipant.conversation_id == class_conv.id,
            ConversationParticipant.user_id == current_user.id
        ).first()
        
        if not existing:
            participant = ConversationParticipant(
                conversation_id=class_conv.id,
                user_id=current_user.id
            )
            db.add(participant)
            db.commit()
    
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

# ==========================================
# SEL SYSTEM ENDPOINTS (from Stage 1)
# ==========================================

@app.get("/sel/categories", response_model=List[SELCategoryResponse])
def get_sel_categories(sel_service: SELBusinessLogic = Depends(get_sel_service)):
    return sel_service.get_categories()

@app.get("/sel/balance", response_model=SELBalanceResponse)
def get_sel_balance(
    current_user: User = Depends(get_current_user), 
    sel_service: SELBusinessLogic = Depends(get_sel_service)
):
    balance = sel_service.get_or_create_balance(current_user.id)
    return balance

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

# SEL Transactions (missing from Stage 2)
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

# ==========================================
# NEW STAGE 2: MESSAGING ENDPOINTS
# ==========================================

@app.post("/conversations/direct")
def create_direct_conversation(
    other_user_id: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or get existing direct conversation between two users."""
    try:
        other_user_uuid = UUID(other_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID utilisateur invalide")
    
    # Check if conversation already exists
    existing = db.query(Conversation).join(ConversationParticipant).filter(
        and_(
            Conversation.type == 'direct',
            ConversationParticipant.user_id.in_([current_user.id, other_user_uuid])
        )
    ).group_by(Conversation.id).having(
        func.count(ConversationParticipant.user_id) == 2
    ).first()
    
    if existing:
        # Check if current user is participant
        is_participant = db.query(ConversationParticipant).filter(
            ConversationParticipant.conversation_id == existing.id,
            ConversationParticipant.user_id == current_user.id
        ).first()
        
        if is_participant:
            return {"conversation_id": str(existing.id), "message": "Conversation existante"}
    
    # Get other user info
    other_user = db.query(User).filter(User.id == other_user_uuid).first()
    if not other_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Create new conversation
    conversation = Conversation(
        name=f"{current_user.first_name} & {other_user.first_name}",
        type='direct',
        created_by=current_user.id
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    # Add participants
    participants = [
        ConversationParticipant(conversation_id=conversation.id, user_id=current_user.id),
        ConversationParticipant(conversation_id=conversation.id, user_id=other_user_uuid)
    ]
    
    for participant in participants:
        db.add(participant)
    
    db.commit()
    
    return {"conversation_id": str(conversation.id), "message": "Conversation créée"}

@app.get("/users/list")
def get_users_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of users for direct messaging (excluding current user)."""
    users = db.query(User).filter(
        and_(User.id != current_user.id, User.is_active == True)
    ).all()
    
    return [{
        "id": str(user.id),
        "name": f"{user.first_name} {user.last_name}",
        "first_name": user.first_name,
        "last_name": user.last_name
    } for user in users]

@app.get("/conversations")
def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's conversations."""
    participations = db.query(ConversationParticipant).filter(
        ConversationParticipant.user_id == current_user.id
    ).all()
    
    conversations = []
    for participation in participations:
        conversation = participation.conversation
        
        # Get last message
        last_message = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(desc(Message.created_at)).first()
        
        conversations.append({
            "id": str(conversation.id),
            "name": conversation.name,
            "type": conversation.type,
            "class_name": conversation.class_name,
            "last_message": {
                "content": last_message.content if last_message else None,
                "created_at": last_message.created_at.isoformat() if last_message else None,
                "user_name": f"{last_message.user.first_name} {last_message.user.last_name}" if last_message else None
            } if last_message else None,
            "unread_count": 0,  # TODO: Calculate based on last_read_at
            "updated_at": conversation.updated_at.isoformat()
        })
    
    return conversations

@app.get("/conversations/{conversation_id}/messages")
def get_conversation_messages(
    conversation_id: UUID,
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages from a conversation."""
    # Verify user is participant
    participant = db.query(ConversationParticipant).filter(
        ConversationParticipant.conversation_id == conversation_id,
        ConversationParticipant.user_id == current_user.id
    ).first()
    
    if not participant:
        raise HTTPException(status_code=403, detail="Accès interdit à cette conversation")
    
    # Get messages
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(desc(Message.created_at)).limit(limit).all()
    
    messages.reverse()  # Oldest first
    
    return [{
        "id": str(msg.id),
        "conversation_id": str(msg.conversation_id),
        "user_id": str(msg.user_id),
        "user_name": f"{msg.user.first_name} {msg.user.last_name}",
        "content": msg.content,
        "message_type": msg.message_type,
        "created_at": msg.created_at.isoformat(),
        "edited_at": msg.edited_at.isoformat() if msg.edited_at else None
    } for msg in messages]

@app.post("/conversations/{conversation_id}/messages")
def send_message_to_conversation(
    conversation_id: UUID,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to a conversation."""
    # Verify user is participant
    participant = db.query(ConversationParticipant).filter(
        ConversationParticipant.conversation_id == conversation_id,
        ConversationParticipant.user_id == current_user.id
    ).first()
    
    if not participant:
        raise HTTPException(status_code=403, detail="Accès interdit à cette conversation")
    
    # Create message
    message = Message(
        conversation_id=conversation_id,
        user_id=current_user.id,
        content=message_data.content.strip(),
        message_type='text'
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # TODO: Send real-time notification via WebSocket
    
    return {
        "id": str(message.id),
        "message": "Message envoyé",
        "created_at": message.created_at.isoformat()
    }

# ==========================================
# NEW STAGE 2: EVENTS ENDPOINTS  
# ==========================================

@app.get("/events")
def get_events(
    event_type: Optional[str] = Query(None),
    class_name: Optional[str] = Query(None),
    upcoming_only: bool = Query(False),
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get school events."""
    print(f"🔍 Events API called by user {current_user.email}")
    
    # Start with all active events
    query = db.query(Event).filter(Event.is_active == True)
    
    # Count total events before filters
    total_events = query.count()
    print(f"🔍 Total active events in DB: {total_events}")
    
    if upcoming_only:
        # Show only future events
        query = query.filter(Event.start_date >= datetime.utcnow())
        print(f"🔍 After upcoming filter: {query.count()} events")
    
    if event_type:
        query = query.filter(Event.event_type == event_type)
        print(f"🔍 After type filter ({event_type}): {query.count()} events")
    
    if class_name:
        query = query.filter(Event.class_name == class_name)
        print(f"🔍 After class filter ({class_name}): {query.count()} events")
    
    events = query.order_by(Event.start_date).limit(limit).all()
    print(f"🔍 Final events to return: {len(events)}")
    
    if not events:
        print("❌ No events found - checking first event in DB...")
        first_event = db.query(Event).first()
        if first_event:
            print(f"📅 First event example: {first_event.title}, active: {first_event.is_active}, date: {first_event.start_date}")
    
    result = []
    for event in events:
        # Check if user is registered
        participant = db.query(EventParticipant).filter(
            EventParticipant.event_id == event.id,
            EventParticipant.user_id == current_user.id
        ).first()
        
        # Count participants
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
            "registration_deadline": event.registration_deadline.isoformat() if event.registration_deadline else None,
            "is_registered": participant is not None,
            "created_by": str(event.created_by),
            "created_at": event.created_at.isoformat()
        })
    
    print(f"✅ Returning {len(result)} events to frontend")
    return result

@app.post("/events/{event_id}/register")
def register_for_event(
    event_id: UUID,
    notes: str = Form(""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register for an event."""
    event = db.query(Event).filter(Event.id == event_id, Event.is_active == True).first()
    if not event:
        raise HTTPException(status_code=404, detail="Événement non trouvé")
    
    # Check if registration is required
    if not event.registration_required:
        raise HTTPException(status_code=400, detail="Inscription non requise pour cet événement")
    
    # Check deadline
    if event.registration_deadline and datetime.utcnow() > event.registration_deadline:
        raise HTTPException(status_code=400, detail="Date limite d'inscription dépassée")
    
    # Check if already registered
    existing = db.query(EventParticipant).filter(
        EventParticipant.event_id == event_id,
        EventParticipant.user_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Déjà inscrit à cet événement")
    
    # Check capacity
    if event.max_participants:
        current_count = db.query(EventParticipant).filter(
            EventParticipant.event_id == event_id,
            EventParticipant.status == 'registered'
        ).count()
        
        if current_count >= event.max_participants:
            raise HTTPException(status_code=400, detail="Événement complet")
    
    # Register user
    participant = EventParticipant(
        event_id=event_id,
        user_id=current_user.id,
        notes=notes
    )
    db.add(participant)
    db.commit()
    
    return {"message": "Inscription confirmée", "event_title": event.title}

# ==========================================
# NEW STAGE 2: WEBSOCKET ENDPOINT
# ==========================================

@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time messaging."""
    try:
        # Verify token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            await websocket.close(code=1008)
            return
        
        user = db.query(User).filter(User.email == email).first()
        if not user:
            await websocket.close(code=1008)
            return
        
        # Connect user
        await websocket_manager.connect(websocket, user.id, db)
        
        # Handle messages
        await websocket_manager.handle_message(websocket, user.id, db)
        
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        await websocket.close(code=1011)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)