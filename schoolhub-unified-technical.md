# SchoolHub - Architecture Technique Unifiée Production-Ready

## 📋 Vue d'ensemble

Plateforme scolaire collaborative open source avec croissance modulaire progressive, adaptée au contexte belge (Evere/Bruxelles).

### Philosophie technique
- **Stage 0** : Auth + Profils (5 familles) → SQLite, pas de Redis
- **Stage 1** : +SEL (30 familles) → PostgreSQL
- **Stage 2** : +Messagerie/Events (60 familles) → Redis, WebSockets
- **Stage 3** : +Boutique/Education (100 familles) → MinIO, Printful
- **Stage 4** : +Multilingual/Analytics (200+ familles) → Full stack

### Stack technique progressive
| Stage | Backend | Frontend | Database | Infra |
|-------|---------|----------|----------|-------|
| **0** | FastAPI minimal | Vue 3 CDN | SQLite | 1 serveur |
| **1** | +Pydantic/Alembic | Vue 3 + Vite | PostgreSQL | Docker |
| **2** | +WebSockets/Celery | +Pinia/PWA | +Redis | Docker Compose |
| **3** | +MinIO/Stripe | +i18n | +Backups | VPS 10€ |
| **4** | +Monitoring | +Analytics | +Replication | K8s ready |

## 🏗️ Architecture Complète (Stage 4)

```mermaid
graph TB
    subgraph "Clients"
        WEB[Vue.js SPA]
        PWA[Progressive Web App]
        MOBILE[React Native - Futur]
    end
    
    subgraph "Gateway Layer"
        NGINX[Nginx Reverse Proxy]
        WAF[ModSecurity WAF]
        RATE[Rate Limiting]
        SSL[Let's Encrypt SSL]
    end
    
    subgraph "Application Layer"
        API[FastAPI Backend]
        WS[WebSocket Server]
        WORKER[Celery Workers]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL 15)]
        REDIS[(Redis Cache)]
        MINIO[MinIO S3]
    end
    
    subgraph "External Services - Belgique"
        MOLLIE[Mollie Payments]
        PRINT[Printful API]
        BPOST[bpost Tracking]
        ITSME[itsme® Auth]
    end
    
    subgraph "Monitoring"
        PROM[Prometheus]
        GRAF[Grafana]
        SENTRY[Sentry]
    end
    
    WEB --> NGINX
    PWA --> NGINX
    NGINX --> WAF
    WAF --> API
    WAF --> WS
    
    API --> PG
    API --> REDIS
    API --> WORKER
    API --> MINIO
    
    WORKER --> REDIS
    WORKER --> PG
    
    API --> MOLLIE
    API --> PRINT
    
    API --> PROM
    PROM --> GRAF
    API --> SENTRY
```

## 📁 Structure du Projet

```bash
schoolhub/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py          # Stage 0
│   │   │   │   ├── users.py         # Stage 0
│   │   │   │   ├── sel.py           # Stage 1
│   │   │   │   ├── messages.py      # Stage 2
│   │   │   │   ├── events.py        # Stage 2
│   │   │   │   ├── shop.py          # Stage 3
│   │   │   │   ├── education.py     # Stage 3
│   │   │   │   └── admin.py         # Stage 4
│   │   │   ├── deps.py
│   │   │   └── router.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── database.py
│   │   │   └── modules.py  # Gestion modules activables
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py     # Stage 0
│   │   │   ├── sel.py      # Stage 1
│   │   │   ├── message.py  # Stage 2
│   │   │   ├── event.py    # Stage 2
│   │   │   ├── shop.py     # Stage 3
│   │   │   └── education.py # Stage 3
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── workers/
│   │   │   ├── tasks.py
│   │   │   └── celery_app.py
│   │   └── main.py
│   ├── tests/
│   ├── alembic/
│   │   └── versions/  # Migrations par stage
│   ├── scripts/
│   │   ├── init_stage0.py
│   │   ├── migrate_to_stage1.py
│   │   └── seed_demo_data.py
│   ├── requirements-stage0.txt  # Minimal
│   ├── requirements-stage1.txt  # +PostgreSQL
│   ├── requirements-stage2.txt  # +Redis, WebSockets
│   ├── requirements-stage3.txt  # +MinIO, Payments
│   ├── requirements-stage4.txt  # Full stack
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── modules/  # Alignés sur les stages backend
│   │   │   ├── core/     # Stage 0
│   │   │   ├── sel/      # Stage 1
│   │   │   ├── messages/ # Stage 2
│   │   │   ├── events/   # Stage 2
│   │   │   ├── shop/     # Stage 3
│   │   │   └── education/# Stage 3
│   │   ├── components/
│   │   ├── views/
│   │   ├── stores/
│   │   ├── locales/
│   │   │   ├── fr-BE.json  # Français Belgique
│   │   │   ├── nl-BE.json  # Néerlandais Belgique
│   │   │   └── en.json
│   │   └── router/
│   ├── public/
│   ├── package.json
│   ├── package-stage0.json  # Vue CDN only
│   └── Dockerfile
├── docker/
│   ├── nginx/
│   │   ├── nginx.conf
│   │   ├── nginx.stage0.conf  # Simple proxy
│   │   └── modsecurity/
│   ├── postgres/
│   │   └── init.sql
│   └── redis/
├── scripts/
│   ├── install-stage0.sh    # Installation minimale
│   ├── upgrade-stage.sh     # Migration entre stages
│   ├── deploy-vps.sh        # Déploiement production
│   ├── backup.sh
│   └── monitoring-setup.sh
├── docs/
│   ├── STAGE0-QUICKSTART.md
│   ├── MIGRATION-GUIDE.md
│   ├── API.md
│   └── BELGIUM-SPECIFIC.md
├── .github/
│   └── workflows/
│       ├── ci-stage0.yml    # Tests minimaux
│       ├── ci-full.yml      # Tests complets
│       └── deploy.yml
├── docker-compose.stage0.yml  # SQLite, pas de Redis
├── docker-compose.stage1.yml  # +PostgreSQL
├── docker-compose.stage2.yml  # +Redis, WebSockets
├── docker-compose.stage3.yml  # +MinIO, workers
├── docker-compose.yml        # Stage 4 complet
├── .env.stage0.example
└── README.md
```

## 🗄️ Modèle de Données Progressif

### Stage 0 : Tables de base (SQLite)

```sql
-- Utilisateurs minimaux
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enfants (optionnel Stage 0, requis Stage 1)
CREATE TABLE children (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER REFERENCES users(id),
    first_name VARCHAR(100) NOT NULL,
    class_name VARCHAR(10), -- P1, P2, P3, P4, P5, P6
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Stage 1 : SEL (Migration vers PostgreSQL)

```sql
-- Migration vers PostgreSQL avec UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users améliorés
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enfants avec classes belges
CREATE TABLE children (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    class_name VARCHAR(10) CHECK (class_name IN ('M1','M2','M3','P1','P2','P3','P4','P5','P6')),
    birth_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE user_children (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    child_id UUID REFERENCES children(id) ON DELETE CASCADE,
    relationship VARCHAR(50) DEFAULT 'parent',
    PRIMARY KEY (user_id, child_id)
);

-- SEL: Services
CREATE TABLE sel_services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    units_per_hour INTEGER DEFAULT 60,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- SEL: Transactions avec limites belges
CREATE TABLE sel_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_user_id UUID REFERENCES users(id),
    to_user_id UUID REFERENCES users(id),
    service_id UUID REFERENCES sel_services(id),
    units INTEGER NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- SEL: Balances avec contraintes
CREATE TABLE sel_balances (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    balance INTEGER DEFAULT 120,
    total_given INTEGER DEFAULT 0,
    total_received INTEGER DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT balance_limits CHECK (balance >= -300 AND balance <= 600)
);
```

### Stage 2+ : Tables additionnelles

```sql
-- Stage 2: Messagerie
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200),
    type VARCHAR(20) CHECK (type IN ('direct', 'group', 'announcement')),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    content TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Stage 2: Événements
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    start_date TIMESTAMPTZ NOT NULL,
    end_date TIMESTAMPTZ,
    location VARCHAR(200),
    max_participants INTEGER,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Stage 3: Boutique simple
CREATE TABLE shop_products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    base_price DECIMAL(10,2) NOT NULL,
    printful_id VARCHAR(100),
    category VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE shop_interests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES shop_products(id),
    user_id UUID REFERENCES users(id),
    quantity INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes performance
CREATE INDEX idx_sel_services_user ON sel_services(user_id);
CREATE INDEX idx_sel_transactions_users ON sel_transactions(from_user_id, to_user_id);
CREATE INDEX idx_messages_conversation ON messages(conversation_id, created_at DESC);
CREATE INDEX idx_events_date ON events(start_date);

-- Trigger updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

## 🚀 Backend FastAPI Progressif

### Stage 0 : Minimal (`backend/app/main.py`)

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os

# Configuration minimale
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./schoolhub.db")
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
ALGORITHM = "HS256"

# Database
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Models minimaux
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

Base.metadata.create_all(bind=engine)

# Schemas Pydantic
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# FastAPI app
app = FastAPI(
    title="SchoolHub Stage 0",
    version="0.1.0",
    description="Version minimale pour démarrer"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints de base
@app.get("/")
def read_root():
    return {"message": "SchoolHub API Stage 0", "status": "running"}

@app.post("/register", response_model=Token)
def register(user: UserRegister, db: Session = Depends(get_db)):
    # Vérifier si l'email existe
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")
    
    # Créer l'utilisateur
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    
    # Créer le token
    access_token = jwt.encode(
        {"sub": user.email, "exp": datetime.utcnow() + timedelta(days=7)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return Token(access_token=access_token)

@app.post("/login", response_model=Token)
def login(email: EmailStr, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    access_token = jwt.encode(
        {"sub": user.email, "exp": datetime.utcnow() + timedelta(days=7)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return Token(access_token=access_token)

@app.get("/health")
def health_check():
    return {"status": "healthy", "stage": 0}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Stage 1+ : Service SEL Complet

```python
# backend/app/services/sel_service.py
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from app.models.sel import SELService, SELTransaction, SELBalance
from app.schemas.sel import ServiceCreate, TransactionCreate
from app.core.exceptions import InsufficientBalanceError

class SELServiceManager:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_service(self, user_id: UUID, data: ServiceCreate) -> SELService:
        service = SELService(user_id=user_id, **data.dict())
        self.db.add(service)
        await self.db.commit()
        await self.db.refresh(service)
        return service
    
    async def create_transaction(
        self,
        from_user_id: UUID,
        data: TransactionCreate
    ) -> SELTransaction:
        # Vérifier les balances
        from_balance = await self._get_or_create_balance(from_user_id)
        to_balance = await self._get_or_create_balance(data.to_user_id)
        
        # Contraintes belges
        if from_balance.balance - data.units < -300:
            raise InsufficientBalanceError("Limite de -300 unités atteinte")
        
        if to_balance.balance + data.units > 600:
            raise InsufficientBalanceError("Le destinataire dépasserait 600 unités")
        
        # Créer la transaction
        transaction = SELTransaction(
            from_user_id=from_user_id,
            to_user_id=data.to_user_id,
            units=data.units,
            description=data.description,
            service_id=data.service_id
        )
        
        # Mettre à jour les balances
        from_balance.balance -= data.units
        from_balance.total_given += data.units
        to_balance.balance += data.units
        to_balance.total_received += data.units
        
        self.db.add(transaction)
        await self.db.commit()
        
        return transaction
    
    async def _get_or_create_balance(self, user_id: UUID) -> SELBalance:
        result = await self.db.execute(
            select(SELBalance).where(SELBalance.user_id == user_id)
        )
        balance = result.scalar_one_or_none()
        
        if not balance:
            # Solde initial : 120 unités (2h)
            balance = SELBalance(user_id=user_id, balance=120)
            self.db.add(balance)
            await self.db.commit()
            await self.db.refresh(balance)
        
        return balance
```

## 🎨 Frontend Vue 3 Progressif

### Stage 0 : HTML + Vue CDN

```html
<!-- frontend/index.html - Stage 0 -->
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SchoolHub - École d'Evere</title>
    <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div id="app" class="min-h-screen bg-gray-50">
        <!-- Header -->
        <header class="bg-white shadow">
            <div class="max-w-7xl mx-auto px-4 py-6">
                <h1 class="text-3xl font-bold text-gray-900">
                    SchoolHub École d'Evere
                </h1>
                <p class="text-gray-600">Plateforme d'entraide entre parents</p>
            </div>
        </header>

        <!-- Content -->
        <main class="max-w-7xl mx-auto px-4 py-8">
            <!-- Login/Register -->
            <div v-if="!isAuthenticated" class="max-w-md mx-auto">
                <div class="bg-white rounded-lg shadow p-6">
                    <h2 class="text-xl font-bold mb-4">
                        {{ isLogin ? 'Connexion' : 'Inscription' }}
                    </h2>
                    
                    <form @submit.prevent="isLogin ? login() : register()">
                        <input
                            v-model="formData.email"
                            type="email"
                            placeholder="Email"
                            class="w-full p-2 border rounded mb-4"
                            required
                        >
                        
                        <input
                            v-if="!isLogin"
                            v-model="formData.firstName"
                            type="text"
                            placeholder="Prénom"
                            class="w-full p-2 border rounded mb-4"
                            required
                        >
                        
                        <input
                            v-if="!isLogin"
                            v-model="formData.lastName"
                            type="text"
                            placeholder="Nom"
                            class="w-full p-2 border rounded mb-4"
                            required
                        >
                        
                        <input
                            v-model="formData.password"
                            type="password"
                            placeholder="Mot de passe"
                            class="w-full p-2 border rounded mb-4"
                            required
                        >
                        
                        <button
                            type="submit"
                            class="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
                        >
                            {{ isLogin ? 'Se connecter' : "S'inscrire" }}
                        </button>
                    </form>
                    
                    <p class="mt-4 text-center text-gray-600">
                        <a
                            href="#"
                            @click.prevent="isLogin = !isLogin"
                            class="text-blue-500 hover:underline"
                        >
                            {{ isLogin ? "Pas encore de compte?" : "Déjà inscrit?" }}
                        </a>
                    </p>
                </div>
            </div>

            <!-- Dashboard -->
            <div v-else>
                <div class="bg-white rounded-lg shadow p-6">
                    <h2 class="text-xl font-bold mb-4">
                        Bienvenue {{ user.firstName }} {{ user.lastName }}!
                    </h2>
                    
                    <p class="text-gray-600 mb-4">
                        Stage 0 : Authentification fonctionnelle ✓
                    </p>
                    
                    <p class="text-gray-600 mb-4">
                        Prochaine étape : SEL (Système d'Échange Local)
                    </p>
                    
                    <button
                        @click="logout"
                        class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
                    >
                        Déconnexion
                    </button>
                </div>
            </div>
        </main>
    </div>

    <script>
        const { createApp } = Vue;
        
        createApp({
            data() {
                return {
                    isLogin: true,
                    isAuthenticated: false,
                    user: null,
                    formData: {
                        email: '',
                        firstName: '',
                        lastName: '',
                        password: ''
                    }
                }
            },
            mounted() {
                // Vérifier si token en localStorage
                const token = localStorage.getItem('token');
                if (token) {
                    this.isAuthenticated = true;
                    // Décoder le JWT pour récupérer l'email
                    const payload = JSON.parse(atob(token.split('.')[1]));
                    this.user = { email: payload.sub };
                }
            },
            methods: {
                async register() {
                    try {
                        const response = await fetch('http://localhost:8000/register', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                email: this.formData.email,
                                first_name: this.formData.firstName,
                                last_name: this.formData.lastName,
                                password: this.formData.password
                            })
                        });
                        
                        if (response.ok) {
                            const data = await response.json();
                            localStorage.setItem('token', data.access_token);
                            this.isAuthenticated = true;
                            this.user = {
                                email: this.formData.email,
                                firstName: this.formData.firstName,
                                lastName: this.formData.lastName
                            };
                        } else {
                            alert('Erreur lors de l\'inscription');
                        }
                    } catch (error) {
                        console.error('Erreur:', error);
                        alert('Erreur de connexion au serveur');
                    }
                },
                
                async login() {
                    try {
                        const formData = new FormData();
                        formData.append('email', this.formData.email);
                        formData.append('password', this.formData.password);
                        
                        const response = await fetch('http://localhost:8000/login', {
                            method: 'POST',
                            body: formData
                        });
                        
                        if (response.ok) {
                            const data = await response.json();
                            localStorage.setItem('token', data.access_token);
                            this.isAuthenticated = true;
                            this.user = { email: this.formData.email };
                        } else {
                            alert('Email ou mot de passe incorrect');
                        }
                    } catch (error) {
                        console.error('Erreur:', error);
                        alert('Erreur de connexion au serveur');
                    }
                },
                
                logout() {
                    localStorage.removeItem('token');
                    this.isAuthenticated = false;
                    this.user = null;
                    this.formData = {
                        email: '',
                        firstName: '',
                        lastName: '',
                        password: ''
                    };
                }
            }
        }).mount('#app');
    </script>
</body>
</html>
```

## 🐳 Docker Compose Progressif

### Stage 0 : Docker Compose Minimal

```yaml
# docker-compose.stage0.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./schoolhub.db
      - SECRET_KEY=${SECRET_KEY:-change-this-in-production}
    volumes:
      - ./backend:/app
      - ./data:/app/data
    command: python app/main.py

  frontend:
    image: nginx:alpine
    ports:
      - "3000:80"
    volumes:
      - ./frontend:/usr/share/nginx/html:ro

volumes:
  data:
```

### Stage 3+ : Production Complete

```yaml
# docker-compose.yml - Stage 4 complet
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: schoolhub
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: schoolhub
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U schoolhub"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ACCESS_KEY}
      MINIO_ROOT_PASSWORD: ${MINIO_SECRET_KEY}
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"
      - "9001:9001"

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://schoolhub:${DB_PASSWORD}@postgres/schoolhub
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      MINIO_ENDPOINT: minio:9000
      SECRET_KEY: ${SECRET_KEY}
      MOLLIE_API_KEY: ${MOLLIE_API_KEY}  # Belgique
      PRINTFUL_API_KEY: ${PRINTFUL_API_KEY}
      SENDGRID_API_KEY: ${SENDGRID_API_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000

  celery:
    build: ./backend
    command: celery -A app.workers.celery_app worker -l info
    environment:
      DATABASE_URL: postgresql://schoolhub:${DB_PASSWORD}@postgres/schoolhub
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
    depends_on:
      - postgres
      - redis

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      VITE_API_URL: ${API_URL:-http://localhost:8000/api/v1}
      VITE_WS_URL: ${WS_URL:-ws://localhost:8000}

  nginx:
    image: nginx:alpine
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certbot/www:/var/www/certbot:ro
      - ./certbot/conf:/etc/nginx/ssl:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
      - frontend

  # Monitoring (Stage 4)
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}

volumes:
  postgres_data:
  redis_data:
  minio_data:
```

## 🔒 Sécurité & DevOps

### GitHub Actions CI/CD Progressif

```yaml
# .github/workflows/ci-stage0.yml
name: CI Stage 0

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  test-minimal:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements-stage0.txt
          pip install pytest
      
      - name: Run basic tests
        run: |
          cd backend
          pytest tests/test_auth.py
      
      - name: Check frontend
        run: |
          # Vérifier que index.html existe
          test -f frontend/index.html
```

### Script de déploiement VPS

```bash
#!/bin/bash
# scripts/deploy-vps.sh

# Configuration
VPS_HOST=${VPS_HOST:-"your-vps-ip"}
VPS_USER=${VPS_USER:-"deploy"}
APP_DIR="/opt/schoolhub"
STAGE=${1:-0}  # Stage par défaut : 0

echo "🚀 Déploiement SchoolHub Stage $STAGE"

# Fonction pour chaque stage
deploy_stage0() {
    echo "📦 Installation Stage 0 (Minimal)"
    ssh $VPS_USER@$VPS_HOST << 'ENDSSH'
    # Installer Docker
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    
    # Clone repo
    git clone https://github.com/your-org/schoolhub.git /opt/schoolhub
    cd /opt/schoolhub
    
    # Configuration minimale
    cp .env.stage0.example .env
    
    # Lancer Stage 0
    docker-compose -f docker-compose.stage0.yml up -d
    
    echo "✅ Stage 0 déployé : http://$VPS_HOST:3000"
ENDSSH
}

deploy_stage1() {
    echo "📦 Upgrade vers Stage 1 (SEL + PostgreSQL)"
    ssh $VPS_USER@$VPS_HOST << 'ENDSSH'
    cd /opt/schoolhub
    
    # Backup SQLite
    docker-compose -f docker-compose.stage0.yml exec backend python scripts/export_to_json.py
    
    # Stop Stage 0
    docker-compose -f docker-compose.stage0.yml down
    
    # Start Stage 1
    docker-compose -f docker-compose.stage1.yml up -d
    
    # Migrate data
    docker-compose -f docker-compose.stage1.yml exec backend python scripts/import_from_json.py
    
    # Run migrations
    docker-compose -f docker-compose.stage1.yml exec backend alembic upgrade head
    
    echo "✅ Stage 1 déployé avec PostgreSQL"
ENDSSH
}

# Exécuter selon le stage
case $STAGE in
    0) deploy_stage0 ;;
    1) deploy_stage1 ;;
    2) deploy_stage2 ;;
    3) deploy_stage3 ;;
    4) deploy_stage4 ;;
    *) echo "❌ Stage invalide: $STAGE" ;;
esac
```

## 📝 Guide de Migration Entre Stages

### Migration Stage 0 → Stage 1

```python
# backend/scripts/migrate_to_stage1.py
import json
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import psycopg2

def migrate_sqlite_to_postgres():
    """Migration des données SQLite vers PostgreSQL"""
    
    # 1. Export depuis SQLite
    conn_sqlite = sqlite3.connect('schoolhub.db')
    cursor = conn_sqlite.cursor()
    
    # Export users
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    # Export children
    cursor.execute("SELECT * FROM children")
    children = cursor.fetchall()
    
    conn_sqlite.close()
    
    # 2. Import vers PostgreSQL
    conn_pg = psycopg2.connect(
        host="postgres",
        database="schoolhub",
        user="schoolhub",
        password=os.environ['DB_PASSWORD']
    )
    cursor_pg = conn_pg.cursor()
    
    # Import users avec UUID
    for user in users:
        cursor_pg.execute("""
            INSERT INTO users (email, first_name, last_name, hashed_password, is_active)
            VALUES (%s, %s, %s, %s, %s)
        """, user[1:])  # Skip l'ID SQLite
    
    # Créer les balances SEL initiales
    cursor_pg.execute("""
        INSERT INTO sel_balances (user_id, balance)
        SELECT id, 120 FROM users
    """)
    
    conn_pg.commit()
    conn_pg.close()
    
    print("✅ Migration Stage 0 → Stage 1 terminée")

if __name__ == "__main__":
    migrate_sqlite_to_postgres()
```

## 🚀 Commandes pour Claude Code

```bash
# DÉMARRAGE RAPIDE STAGE 0 (30 minutes)
mkdir schoolhub && cd schoolhub

# 1. Backend minimal
mkdir -p backend/app
cat > backend/requirements-stage0.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic[email]==2.5.0
EOF

# Copier le code main.py du Stage 0 depuis l'artifact

# 2. Frontend minimal
mkdir frontend
# Copier index.html depuis l'artifact

# 3. Docker
# Copier docker-compose.stage0.yml

# 4. Lancer
docker-compose -f docker-compose.stage0.yml up

# 5. Tester
curl http://localhost:8000/health
# Ouvrir http://localhost:3000

# PROGRESSION VERS STAGE 1
./scripts/upgrade-stage.sh 1

# AJOUT MODULE SEL
docker-compose exec backend python scripts/enable_module.py sel

# TESTS
docker-compose exec backend pytest tests/

# BACKUP
docker-compose exec postgres pg_dump -U schoolhub schoolhub > backup.sql
```

## 📊 Métriques de Succès par Stage

| Stage | Utilisateurs | Transactions/mois | Uptime | Temps réponse |
|-------|-------------|-------------------|---------|---------------|
| **0** | 5-10 | - | 95% | <500ms |
| **1** | 20-30 | 50 | 98% | <300ms |
| **2** | 40-60 | 200 | 99% | <200ms |
| **3** | 80-100 | 500 | 99.5% | <150ms |
| **4** | 200+ | 1000+ | 99.9% | <100ms |

## ✅ Checklist de Production

### Stage 0 - Lancement
- [ ] Auth fonctionne
- [ ] HTTPS (Let's Encrypt)
- [ ] Backup SQLite quotidien
- [ ] 5 familles test

### Stage 1 - SEL Actif
- [ ] PostgreSQL migré
- [ ] Limites -300/+600
- [ ] 30 familles inscrites
- [ ] 50 transactions/mois

### Stage 2 - Communication
- [ ] WebSockets stable
- [ ] Redis cache actif
- [ ] Notifications email
- [ ] 60 familles actives

### Stage 3 - Commerce
- [ ] Mollie intégré (BE)
- [ ] Printful connecté
- [ ] MinIO pour images
- [ ] 100 familles

### Stage 4 - Scale
- [ ] Monitoring complet
- [ ] Multi-langue (FR/NL/EN)
- [ ] Analytics dashboard
- [ ] 200+ familles

## 🎯 Points Clés Belgique

- **Classes** : M1-M3 (maternelle), P1-P6 (primaire)
- **CEB** : Certificat en P6
- **Paiements** : Mollie (compatible Bancontact)
- **Langues** : FR/NL obligatoire, EN souhaitable
- **RGPD** : Strict dès le Stage 0
- **Hébergement** : OVH Belgique recommandé