import os
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import Depends, FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import Boolean, Column, DateTime, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

# Configuration minimale
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./db/ecolehub.db")
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production-very-important")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

# Database
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Models SQLAlchemy
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Child(Base):
    __tablename__ = "children"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, nullable=False)
    first_name = Column(String, nullable=False)
    class_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# Créer les tables
Base.metadata.create_all(bind=engine)


# Schemas Pydantic
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class ChildCreate(BaseModel):
    first_name: str
    class_name: str


class ChildResponse(BaseModel):
    id: int
    first_name: str
    class_name: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# FastAPI app
app = FastAPI(
    title="EcoleHub Stage 0",
    version="0.1.0",
    description="Plateforme scolaire collaborative - EcoleHub",
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


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


# Endpoints
@app.get("/")
def read_root():
    return {
        "message": "EcoleHub API Stage 0",
        "status": "running",
        "école": "EcoleHub",
        "version": "0.1.0",
    }


@app.post("/register", response_model=Token)
def register(user: UserRegister, db: Session = Depends(get_db)):
    # Vérifier si l'email existe déjà
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")

    # Créer l'utilisateur
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

    # Créer le token
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


@app.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.put("/me", response_model=UserResponse)
def update_users_me(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if first_name:
        current_user.first_name = first_name
    if last_name:
        current_user.last_name = last_name

    db.commit()
    db.refresh(current_user)
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
    # Valider la classe belge
    valid_classes = ["M1", "M2", "M3", "P1", "P2", "P3", "P4", "P5", "P6"]
    if child.class_name not in valid_classes:
        raise HTTPException(
            status_code=400,
            detail=f"Classe invalide. Classes valides: {', '.join(valid_classes)}",
        )

    db_child = Child(
        parent_id=current_user.id,
        first_name=child.first_name,
        class_name=child.class_name,
    )
    db.add(db_child)
    db.commit()
    db.refresh(db_child)
    return db_child


@app.delete("/children/{child_id}")
def delete_child(
    child_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    child = (
        db.query(Child)
        .filter(Child.id == child_id, Child.parent_id == current_user.id)
        .first()
    )

    if not child:
        raise HTTPException(status_code=404, detail="Enfant non trouvé")

    db.delete(child)
    db.commit()
    return {"message": "Enfant supprimé"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "stage": 0, "database": "SQLite", "école": "EcoleHub"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
