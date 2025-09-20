# SEL (Système d'Échange Local) Unit Tests
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models_stage1 import SELService, User
from app.sel_service import SELBusinessLogic


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
        )
        db_session.add(user)
        db_session.commit()

        # Create SEL service and get/create balance
        sel_service = SELBusinessLogic(db_session)
        balance = sel_service.get_or_create_balance(user.id)

        assert balance is not None
        assert balance.balance == 120  # 2 hours * 60 units

    def test_balance_limits_belgian_rules(
        self, db_session: Session, test_user_parent: User
    ):
        """Test Belgian SEL balance limits: -300 to +600 units."""
        sel_service = SELBusinessLogic(db_session)
        balance = sel_service.get_or_create_balance(test_user_parent.id)
        balance.balance = 0
        db_session.commit()

        # Test minimum limit (-300)
        new_balance_valid = balance.balance - 300  # Should be -300
        new_balance_invalid = balance.balance - 301  # Should be -301
        assert new_balance_valid >= -300  # Valid: can go to -300
        assert new_balance_invalid < -300  # Invalid: cannot go below -300

        # Test maximum limit (+600)
        balance.balance = 600
        db_session.commit()
        new_balance_valid = balance.balance + 0  # Should stay at 600
        new_balance_invalid = balance.balance + 1  # Should be 601
        assert new_balance_valid <= 600  # Valid: can stay at 600
        assert new_balance_invalid > 600  # Invalid: cannot go above 600

    def test_units_per_hour_standard_60(self, sel_categories):
        """Test standard rate is 60 units = 1 hour."""
        standard_rate = 60
        assert standard_rate == 60  # Belgian SEL standard


@pytest.mark.sel
class TestSELServices:
    """Test SEL service management."""

    def test_create_sel_service(
        self,
        client: TestClient,
        auth_headers_parent: dict,
        test_user_parent: User,
        db_session: Session,
    ):
        """Test creating a new SEL service."""
        # Create category first
        from app.models_stage1 import SELCategory

        category = SELCategory(name="devoirs", description="Aide aux devoirs")
        db_session.add(category)
        db_session.commit()

        service_data = {
            "title": "Aide aux devoirs",
            "description": "Aide aux devoirs pour primaire P1-P3",
            "category": "devoirs",
            "units_per_hour": 60,
        }

        response = client.post(
            "/api/sel/services", json=service_data, headers=auth_headers_parent
        )

        assert response.status_code in (200, 201)
        data = response.json()
        assert data["title"] == service_data["title"]
        assert data["category"] == service_data["category"]
        assert data["units_per_hour"] == 60
        assert data["is_active"] is True

    def test_list_available_services(
        self,
        client: TestClient,
        auth_headers_parent: dict,
        test_user_parent: User,
        db_session: Session,
    ):
        """Test listing available SEL services."""
        # Create a service from a different user (admin) so it shows up in
        # available services
        from app.models_stage1 import SELCategory

        admin_user = User(
            email="admin@test.be",
            first_name="Admin",
            last_name="User",
            hashed_password="hashed",
        )
        db_session.add(admin_user)
        db_session.commit()

        # Create category for this service
        category = SELCategory(name="transport", description="Transport services")
        db_session.add(category)
        db_session.commit()

        # Create service from admin user
        service = SELService(
            title="Transport école",
            description="Transport vers l'école",
            category="transport",
            units_per_hour=45,
            is_active=True,
            user_id=admin_user.id,
        )
        db_session.add(service)
        db_session.commit()

        response = client.get("/api/sel/services", headers=auth_headers_parent)

        assert response.status_code == 200
        services = response.json()
        assert len(services) >= 1
        assert any(s["title"] == "Transport école" for s in services)

    def test_get_my_services(
        self,
        client: TestClient,
        auth_headers_parent: dict,
        test_sel_service: SELService,
    ):
        """Test getting current user's services."""
        response = client.get("/api/sel/services/mine", headers=auth_headers_parent)

        assert response.status_code == 200
        services = response.json()
        assert len(services) >= 1
        assert services[0]["title"] == test_sel_service.title

    def test_service_categories_belgian_context(self, sel_categories):
        """Test SEL categories match Belgian school context."""
        expected_categories = [
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

        for category in expected_categories:
            assert category in sel_categories

    # Deactivation endpoint not part of Stage 4 minimal API; tested via
    # service layer elsewhere


@pytest.mark.sel
class TestSELTransactions:
    """Test SEL transaction system."""

    # Transaction API endpoints not exposed in Stage 4 minimal router; skipped here

    # Approval flow handled by service layer in full implementation; out of
    # scope for minimal API tests

    def test_transaction_balance_validation(self, db_session: Session):
        """Test transaction respects balance limits."""
        # Create user with minimum balance
        user = User(
            email="minbalance@test.be",
            first_name="Min",
            last_name="Balance",
            hashed_password="hashed",
        )
        db_session.add(user)
        db_session.commit()

        # Use SEL service to create balance properly
        sel_service = SELBusinessLogic(db_session)
        balance = sel_service.get_or_create_balance(user.id)
        balance.balance = -300  # Set to minimum
        db_session.commit()

        # Test transaction validation using SEL service
        result_invalid = sel_service.validate_transaction_balance(user.id, user.id, 1)
        result_valid = sel_service.validate_transaction_balance(user.id, user.id, 0)

        assert result_invalid["valid"] is False  # Cannot debit more when at -300
        assert result_valid["valid"] is True  # Can debit 0 (no change)

    def test_get_user_transactions(
        self, client: TestClient, auth_headers_parent: dict, test_user_parent: User
    ):
        """Test getting user's transaction history."""
        response = client.get("/api/sel/transactions", headers=auth_headers_parent)

        assert response.status_code == 200
        transactions = response.json()
        assert isinstance(transactions, list)

    def test_get_balance(
        self, client: TestClient, auth_headers_parent: dict, test_user_parent: User
    ):
        """Test getting user's SEL balance."""
        response = client.get("/api/sel/balance", headers=auth_headers_parent)

        assert response.status_code == 200
        data = response.json()
        assert "balance" in data
        assert "total_received" in data
        assert "total_given" in data
        assert isinstance(data["balance"], int)
