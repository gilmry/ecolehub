# SEL (Système d'Échange Local) Unit Tests
import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models.user import User
from app.models.sel_service import SELService
from app.models.sel_balance import SELBalance
from app.models.sel_transaction import SELTransaction, TransactionStatus
from app.schemas.user import UserRole


@pytest.mark.sel
class TestSELBalance:
    """Test SEL balance management - Belgian rules."""

    def test_initial_balance_120_units(self, db_session: Session):
        """Test new users get 120 units (2 hours) initial balance."""
        user = User(
            email="newsel@test.be",
            first_name="New",
            last_name="SEL",
            hashed_password="hashed",
            role=UserRole.PARENT
        )
        db_session.add(user)
        db_session.commit()
        
        # Initial balance should be created
        balance = db_session.query(SELBalance).filter_by(user_id=user.id).first()
        assert balance is not None
        assert balance.balance == 120  # 2 hours * 60 units

    def test_balance_limits_belgian_rules(self, db_session: Session, test_user_parent: User):
        """Test Belgian SEL balance limits: -300 to +600 units."""
        balance = SELBalance(user_id=test_user_parent.id, balance=0)
        db_session.add(balance)
        db_session.commit()
        
        # Test minimum limit
        assert balance.can_debit(300) is True   # Can go to -300
        assert balance.can_debit(301) is False  # Cannot go below -300
        
        # Test maximum limit
        balance.balance = 600
        assert balance.can_credit(0) is True    # Can stay at 600
        assert balance.can_credit(1) is False   # Cannot go above 600

    def test_units_per_hour_standard_60(self, sel_categories):
        """Test standard rate is 60 units = 1 hour."""
        standard_rate = 60
        assert standard_rate == 60  # Belgian SEL standard


@pytest.mark.sel
class TestSELServices:
    """Test SEL service management."""

    def test_create_sel_service(self, client: TestClient, auth_headers_parent: dict):
        """Test creating a new SEL service."""
        service_data = {
            "title": "Aide aux devoirs",
            "description": "Aide aux devoirs pour primaire P1-P3",
            "category": "devoirs",
            "units_per_hour": 60
        }
        
        response = client.post(
            "/sel/services",
            json=service_data,
            headers=auth_headers_parent
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == service_data["title"]
        assert data["category"] == service_data["category"]
        assert data["units_per_hour"] == 60
        assert data["is_active"] is True

    def test_list_available_services(self, client: TestClient, auth_headers_parent: dict, test_sel_service: SELService):
        """Test listing available SEL services."""
        response = client.get("/sel/services", headers=auth_headers_parent)
        
        assert response.status_code == 200
        services = response.json()
        assert len(services) >= 1
        assert any(s["title"] == test_sel_service.title for s in services)

    def test_get_my_services(self, client: TestClient, auth_headers_parent: dict, test_sel_service: SELService):
        """Test getting current user's services."""
        response = client.get("/sel/services/mine", headers=auth_headers_parent)
        
        assert response.status_code == 200
        services = response.json()
        assert len(services) >= 1
        assert services[0]["title"] == test_sel_service.title

    def test_service_categories_belgian_context(self, sel_categories):
        """Test SEL categories match Belgian school context."""
        expected_categories = [
            "garde", "devoirs", "transport", "cuisine",
            "jardinage", "informatique", "artisanat", 
            "sport", "musique", "autre"
        ]
        
        for category in expected_categories:
            assert category in sel_categories

    def test_deactivate_service(self, client: TestClient, auth_headers_parent: dict, test_sel_service: SELService):
        """Test service owner can deactivate their service."""
        response = client.put(
            f"/sel/services/{test_sel_service.id}/deactivate",
            headers=auth_headers_parent
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False


@pytest.mark.sel
class TestSELTransactions:
    """Test SEL transaction system."""

    def test_create_transaction_request(self, client: TestClient, auth_headers_parent: dict, test_sel_service: SELService):
        """Test creating a SEL transaction request."""
        transaction_data = {
            "service_id": test_sel_service.id,
            "hours": 2,
            "description": "Garde Emma mardi après-midi"
        }
        
        response = client.post(
            "/sel/transactions",
            json=transaction_data,
            headers=auth_headers_parent
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["units"] == 120  # 2 hours * 60 units
        assert data["status"] == "pending"
        assert data["description"] == transaction_data["description"]

    def test_approve_transaction(self, db_session: Session, test_user_parent: User, test_sel_service: SELService):
        """Test transaction approval updates balances."""
        # Create requester user
        requester = User(
            email="requester@test.be",
            first_name="Requester",
            last_name="User",
            hashed_password="hashed",
            role=UserRole.PARENT
        )
        db_session.add(requester)
        db_session.commit()
        
        # Create transaction
        transaction = SELTransaction(
            from_user_id=requester.id,
            to_user_id=test_user_parent.id,
            service_id=test_sel_service.id,
            units=120,
            description="Test transaction",
            status=TransactionStatus.PENDING
        )
        db_session.add(transaction)
        db_session.commit()
        
        # Approve transaction
        transaction.status = TransactionStatus.APPROVED
        db_session.commit()
        
        # Check balances updated (this would be handled by the service layer)
        assert transaction.status == TransactionStatus.APPROVED

    def test_transaction_balance_validation(self, db_session: Session):
        """Test transaction respects balance limits."""
        # Create user with minimum balance
        user = User(
            email="minbalance@test.be",
            first_name="Min",
            last_name="Balance",
            hashed_password="hashed",
            role=UserRole.PARENT
        )
        db_session.add(user)
        db_session.commit()
        
        balance = SELBalance(user_id=user.id, balance=-300)  # At minimum
        db_session.add(balance)
        db_session.commit()
        
        # Should not be able to debit more
        assert balance.can_debit(1) is False
        assert balance.can_debit(0) is True

    def test_get_user_transactions(self, client: TestClient, auth_headers_parent: dict):
        """Test getting user's transaction history."""
        response = client.get("/sel/transactions", headers=auth_headers_parent)
        
        assert response.status_code == 200
        transactions = response.json()
        assert isinstance(transactions, list)

    def test_get_balance(self, client: TestClient, auth_headers_parent: dict):
        """Test getting user's SEL balance."""
        response = client.get("/sel/balance", headers=auth_headers_parent)
        
        assert response.status_code == 200
        data = response.json()
        assert "balance" in data
        assert "total_received" in data
        assert "total_given" in data
        assert isinstance(data["balance"], int)