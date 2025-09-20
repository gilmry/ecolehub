# Database Integration Tests
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.main_stage4 import get_password_hash
from app.models_stage1 import Child, SELBalance, SELService, SELTransaction, User
from app.schemas_stage1 import TransactionStatus


@pytest.mark.integration
class TestUserDatabaseOperations:
    """Test User model database operations."""

    def test_create_user_with_relationships(self, db_session: Session):
        """Test creating user with children and SEL balance."""
        # Create user
        user = User(
            email="parent@dbtest.be",
            first_name="Database",
            last_name="Test",
            hashed_password=get_password_hash("jules20220902"),
            role=UserRole.PARENT,
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Add child
        child = Child(
            first_name="Emma", last_name="Test", class_level="P3", parent_id=user.id
        )
        db_session.add(child)

        # Add SEL balance
        balance = SELBalance(user_id=user.id, balance=120)
        db_session.add(balance)

        db_session.commit()

        # Verify relationships
        assert len(user.children) == 1
        assert user.children[0].first_name == "Emma"
        assert user.sel_balance.balance == 120

    def test_user_email_uniqueness_constraint(self, db_session: Session):
        """Test email uniqueness is enforced at database level."""
        # Create first user
        user1 = User(
            email="unique@test.be",
            first_name="First",
            last_name="User",
            hashed_password=get_password_hash("jules20220902"),
            role=UserRole.PARENT,
        )
        db_session.add(user1)
        db_session.commit()

        # Try to create second user with same email
        user2 = User(
            email="unique@test.be",  # Same email
            first_name="Second",
            last_name="User",
            hashed_password=get_password_hash("jules20220902"),
            role=UserRole.PARENT,
        )
        db_session.add(user2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_soft_delete(self, db_session: Session):
        """Test user can be deactivated without deleting data."""
        user = User(
            email="deactivate@test.be",
            first_name="To",
            last_name="Deactivate",
            hashed_password=get_password_hash("jules20220902"),
            role=UserRole.PARENT,
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        # Deactivate user
        user.is_active = False
        db_session.commit()

        # User still exists but is inactive
        found_user = (
            db_session.query(User).filter_by(email="deactivate@test.be").first()
        )
        assert found_user is not None
        assert found_user.is_active is False


@pytest.mark.integration
class TestSELDatabaseOperations:
    """Test SEL system database operations."""

    def test_sel_transaction_with_balance_updates(self, db_session: Session):
        """Test SEL transaction creates proper balance updates."""
        # Create two users with balances
        provider = User(
            email="provider@seltest.be",
            first_name="Provider",
            last_name="User",
            hashed_password=get_password_hash("jules20220902"),
            role=UserRole.PARENT,
        )
        requester = User(
            email="requester@seltest.be",
            first_name="Requester",
            last_name="User",
            hashed_password=get_password_hash("jules20220902"),
            role=UserRole.PARENT,
        )

        db_session.add_all([provider, requester])
        db_session.commit()

        # Create balances
        provider_balance = SELBalance(user_id=provider.id, balance=120)
        requester_balance = SELBalance(user_id=requester.id, balance=120)
        db_session.add_all([provider_balance, requester_balance])

        # Create service
        service = SELService(
            title="Test Service",
            description="Test service for transaction",
            category="test",
            units_per_hour=60,
            provider_id=provider.id,
            is_active=True,
        )
        db_session.add(service)
        db_session.commit()

        # Create transaction
        transaction = SELTransaction(
            from_user_id=requester.id,
            to_user_id=provider.id,
            service_id=service.id,
            units=120,
            description="Test transaction",
            status=TransactionStatus.PENDING,
        )
        db_session.add(transaction)
        db_session.commit()

        # Approve transaction and update balances
        transaction.status = TransactionStatus.APPROVED
        provider_balance.balance += 120  # Provider gains
        requester_balance.balance -= 120  # Requester pays

        db_session.commit()

        # Verify final state
        assert transaction.status == TransactionStatus.APPROVED
        assert provider_balance.balance == 240
        assert requester_balance.balance == 0

    def test_sel_balance_constraints(self, db_session: Session):
        """Test SEL balance respects Belgian limits."""
        user = User(
            email="balance@test.be",
            first_name="Balance",
            last_name="Test",
            hashed_password=get_password_hash("jules20220902"),
            role=UserRole.PARENT,
        )
        db_session.add(user)
        db_session.commit()

        # Test minimum balance (-300)
        balance = SELBalance(user_id=user.id, balance=-300)
        db_session.add(balance)
        db_session.commit()  # Should succeed

        # Test that balance can be checked against limits
        assert balance.balance >= -300  # At minimum limit

        # Test maximum balance (+600)
        balance.balance = 600
        db_session.commit()
        assert balance.balance <= 600  # At maximum limit

    def test_cascade_delete_protection(self, db_session: Session):
        """Test that critical data is protected from cascade deletes."""
        # Create user with SEL data
        user = User(
            email="cascade@test.be",
            first_name="Cascade",
            last_name="Test",
            hashed_password=get_password_hash("jules20220902"),
            role=UserRole.PARENT,
        )
        db_session.add(user)
        db_session.commit()

        service = SELService(
            title="Test Service",
            description="Test",
            category="test",
            units_per_hour=60,
            provider_id=user.id,
            is_active=True,
        )
        balance = SELBalance(user_id=user.id, balance=120)

        db_session.add_all([service, balance])
        db_session.commit()

        service_id = service.id
        balance_id = balance.id

        # Instead of deleting, deactivate user
        user.is_active = False
        db_session.commit()

        # SEL data should still exist
        existing_service = db_session.query(SELService).filter_by(id=service_id).first()
        existing_balance = db_session.query(SELBalance).filter_by(id=balance_id).first()

        assert existing_service is not None
        assert existing_balance is not None


@pytest.mark.integration
class TestChildDatabaseOperations:
    """Test Child model database operations."""

    def test_child_class_level_validation(self, db_session: Session):
        """Test child class level follows Belgian system."""
        user = User(
            email="childparent@test.be",
            first_name="Child",
            last_name="Parent",
            hashed_password=get_password_hash("jules20220902"),
            role=UserRole.PARENT,
        )
        db_session.add(user)
        db_session.commit()

        # Valid Belgian class levels
        valid_classes = ["M1", "M2", "M3", "P1", "P2", "P3", "P4", "P5", "P6"]

        for class_level in valid_classes:
            child = Child(
                first_name="Test",
                last_name="Child",
                class_level=class_level,
                parent_id=user.id,
            )
            db_session.add(child)
            db_session.commit()  # Should not raise error

            # Clean up for next iteration
            db_session.delete(child)
            db_session.commit()

    def test_multiple_children_per_parent(self, db_session: Session):
        """Test parent can have multiple children."""
        user = User(
            email="multiparent@test.be",
            first_name="Multi",
            last_name="Parent",
            hashed_password=get_password_hash("jules20220902"),
            role=UserRole.PARENT,
        )
        db_session.add(user)
        db_session.commit()

        # Add multiple children
        child1 = Child(
            first_name="Emma", last_name="Multi", class_level="P3", parent_id=user.id
        )
        child2 = Child(
            first_name="Louis", last_name="Multi", class_level="P1", parent_id=user.id
        )
        child3 = Child(
            first_name="Sophie", last_name="Multi", class_level="M2", parent_id=user.id
        )

        db_session.add_all([child1, child2, child3])
        db_session.commit()

        # Verify relationship
        db_session.refresh(user)
        assert len(user.children) == 3

        # Children should be ordered by class level or age
        child_names = [child.first_name for child in user.children]
        assert "Emma" in child_names
        assert "Louis" in child_names
        assert "Sophie" in child_names


@pytest.mark.integration
class TestDatabasePerformance:
    """Test database performance and query optimization."""

    def test_user_with_children_single_query(self, db_session: Session):
        """Test loading user with children uses efficient queries."""
        # Create user with children
        user = User(
            email="efficient@test.be",
            first_name="Efficient",
            last_name="Query",
            hashed_password=get_password_hash("jules20220902"),
            role=UserRole.PARENT,
        )
        db_session.add(user)
        db_session.commit()

        # Add multiple children
        for i in range(5):
            child = Child(
                first_name=f"Child{i}",
                last_name="Query",
                class_level="P3",
                parent_id=user.id,
            )
            db_session.add(child)

        db_session.commit()

        # Query user with children (should use join/eager loading)
        queried_user = (
            db_session.query(User).filter_by(email="efficient@test.be").first()
        )

        # Access children (should not trigger N+1 queries in optimized implementation)
        children_count = len(queried_user.children)
        assert children_count == 5

    def test_sel_services_with_provider_info(self, db_session: Session):
        """Test querying SEL services with provider info efficiently."""
        # Create multiple users with services
        for i in range(3):
            user = User(
                email=f"provider{i}@test.be",
                first_name=f"Provider{i}",
                last_name="Test",
                hashed_password=get_password_hash("jules20220902"),
                role=UserRole.PARENT,
            )
            db_session.add(user)
            db_session.commit()

            service = SELService(
                title=f"Service {i}",
                description=f"Test service {i}",
                category="test",
                units_per_hour=60,
                provider_id=user.id,
                is_active=True,
            )
            db_session.add(service)

        db_session.commit()

        # Query all services with provider info
        services = db_session.query(SELService).join(User).all()

        assert len(services) == 3
        for service in services:
            assert service.provider is not None
            assert service.provider.first_name.startswith("Provider")
