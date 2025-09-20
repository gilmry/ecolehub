# EcoleHub Test Configuration & Fixtures
import os
import pytest
from typing import Generator, Any
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Set test environment
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "sqlite:///test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"

from app.main_stage4 import app, Base, get_db, get_password_hash
from app.models_stage1 import User, SELService, Child


# Test Database Setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create FastAPI test client with test database."""
    def get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = get_test_db
    
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
        is_active=True
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
        is_active=True
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
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_child(db_session: Session, test_user_parent: User) -> Child:
    """Create test child."""
    child = Child(
        first_name="Emma",
        class_name="P3",
        parent_id=test_user_parent.id
    )
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
        user_id=test_user_parent.id
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)
    return service


# Authentication Fixtures
@pytest.fixture
def auth_headers_parent(client: TestClient) -> dict:
    """Get authentication headers for parent user."""
    response = client.post(
        "/login",
        data={"email": "parent@test.be", "password": "jules20220902"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_admin(client: TestClient) -> dict:
    """Get authentication headers for admin user."""
    response = client.post(
        "/login",
        data={"email": "admin@test.be", "password": "jules20220902"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_direction(client: TestClient) -> dict:
    """Get authentication headers for direction user."""
    response = client.post(
        "/login",
        data={"email": "direction@test.be", "password": "jules20220902"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# Belgian-specific test data
@pytest.fixture
def belgian_classes():
    """Belgian school class levels."""
    return {
        "maternelle": ["M1", "M2", "M3"],
        "primaire": ["P1", "P2", "P3", "P4", "P5", "P6"]
    }


@pytest.fixture
def sel_categories():
    """SEL service categories for Belgian context."""
    return [
        "garde", "devoirs", "transport", "cuisine", 
        "jardinage", "informatique", "artisanat", 
        "sport", "musique", "autre"
    ]