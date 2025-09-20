# EcoleHub Test Configuration & Fixtures
import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Set test environment BEFORE importing the app
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "sqlite:///test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"

from app.main_stage4 import (  # noqa: E402
    Base,
    app,
    create_access_token,
    get_db,
    get_password_hash,
    get_redis,
)
from app.models_stage1 import Child, SELService, User  # noqa: E402

# Test Database Setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)


@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine."""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


class FakeRedis:
    def __init__(self):
        self._store = {}

    def lpush(self, key, value):
        self._store.setdefault(key, []).insert(0, value)

    def expire(self, key, seconds):
        # No-op for tests
        return True

    def keys(self, pattern: str):
        # Minimal pattern support for 'session:*'
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            return [k for k in self._store if k.startswith(prefix)]
        return [k for k in self._store if k == pattern]

    def ping(self):
        return True


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create FastAPI test client with test database and fake Redis."""

    def get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = get_test_db
    app.dependency_overrides[get_redis] = lambda: FakeRedis()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# User Fixtures
@pytest.fixture
def test_user_parent(db_session: Session) -> User:
    """Create test parent user."""
    user = User(
        email="parent@test.be",
        first_name="Marie",
        last_name="Dupont",
        hashed_password=get_password_hash("jules20220902"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user_admin(db_session: Session) -> User:
    """Create test admin user."""
    user = User(
        email="admin@test.be",
        first_name="Admin",
        last_name="EcoleHub",
        hashed_password=get_password_hash("jules20220902"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user_direction(db_session: Session) -> User:
    """Create test direction user."""
    user = User(
        email="direction@test.be",
        first_name="Direction",
        last_name="EcoleHub",
        hashed_password=get_password_hash("jules20220902"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_child(db_session: Session, test_user_parent: User) -> Child:
    """Create test child."""
    child = Child(first_name="Emma", class_name="P3", parent_id=test_user_parent.id)
    db_session.add(child)
    db_session.commit()
    db_session.refresh(child)
    return child


@pytest.fixture
def test_sel_service(db_session: Session, test_user_parent: User) -> SELService:
    """Create test SEL service."""
    service = SELService(
        title="Garde après école",
        description="Garde d'enfants après l'école jusqu'à 18h",
        category="garde",
        units_per_hour=60,
        is_active=True,
        user_id=test_user_parent.id,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)
    return service


# Authentication Fixtures
@pytest.fixture
def auth_headers_parent() -> dict:
    """Get authentication headers for parent user (direct token)."""
    token = create_access_token({"sub": "parent@test.be"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_admin() -> dict:
    """Get authentication headers for admin user (direct token)."""
    token = create_access_token({"sub": "admin@test.be"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_direction() -> dict:
    """Get authentication headers for direction user (direct token)."""
    token = create_access_token({"sub": "direction@test.be"})
    return {"Authorization": f"Bearer {token}"}


# Belgian-specific test data
@pytest.fixture
def belgian_classes():
    """Belgian school class levels."""
    return {
        "maternelle": ["M1", "M2", "M3"],
        "primaire": ["P1", "P2", "P3", "P4", "P5", "P6"],
    }


@pytest.fixture
def sel_categories():
    """SEL service categories for Belgian context."""
    return [
        "garde",
        "devoirs",
        "transport",
        "cuisine",
        "jardinage",
        "informatique",
        "artisanat",
        "sport",
        "musique",
        "autre",
    ]
