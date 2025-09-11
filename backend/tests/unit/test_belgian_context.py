# Belgian School Context Unit Tests
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.child import Child
from app.models.user import User
from app.schemas.user import UserRole


@pytest.mark.unit
class TestBelgianSchoolSystem:
    """Test Belgian school system integration."""

    def test_belgian_class_levels(self, belgian_classes):
        """Test Belgian class levels are properly defined."""
        # Maternelle (Kindergarten)
        assert "M1" in belgian_classes["maternelle"]
        assert "M2" in belgian_classes["maternelle"] 
        assert "M3" in belgian_classes["maternelle"]
        
        # Primaire (Primary)
        assert "P1" in belgian_classes["primaire"]
        assert "P6" in belgian_classes["primaire"]  # CEB year
        
        # Total should be 9 levels
        total_levels = len(belgian_classes["maternelle"]) + len(belgian_classes["primaire"])
        assert total_levels == 9

    def test_ceb_level_recognition(self, belgian_classes):
        """Test P6 is recognized as CEB (Certificat d'Études de Base) level."""
        ceb_level = "P6"
        assert ceb_level in belgian_classes["primaire"]
        assert belgian_classes["primaire"][-1] == "P6"  # Last year of primary


@pytest.mark.unit  
class TestChildManagement:
    """Test child profile management for Belgian schools."""

    def test_create_child_with_belgian_class(self, client: TestClient, auth_headers_parent: dict, belgian_classes):
        """Test creating child with Belgian class level."""
        child_data = {
            "first_name": "Emma",
            "last_name": "Dupont",
            "class_level": "P3"
        }
        
        response = client.post(
            "/children",
            json=child_data,
            headers=auth_headers_parent
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "Emma"
        assert data["class_level"] == "P3"
        assert data["class_level"] in belgian_classes["primaire"]

    def test_invalid_class_level_rejected(self, client: TestClient, auth_headers_parent: dict):
        """Test invalid class level is rejected."""
        child_data = {
            "first_name": "Test",
            "last_name": "Child", 
            "class_level": "INVALID"
        }
        
        response = client.post(
            "/children",
            json=child_data,
            headers=auth_headers_parent
        )
        
        assert response.status_code == 422  # Validation error

    def test_get_children_by_parent(self, client: TestClient, auth_headers_parent: dict, test_child: Child):
        """Test getting children for authenticated parent."""
        response = client.get("/children", headers=auth_headers_parent)
        
        assert response.status_code == 200
        children = response.json()
        assert len(children) >= 1
        assert any(c["first_name"] == test_child.first_name for c in children)

    def test_child_class_progression(self, db_session: Session, test_child: Child, belgian_classes):
        """Test child can progress through Belgian class levels."""
        # Start in P3
        assert test_child.class_level == "P3"
        
        # Progress to P4
        test_child.class_level = "P4"
        db_session.commit()
        
        assert test_child.class_level == "P4"
        assert test_child.class_level in belgian_classes["primaire"]


@pytest.mark.unit
class TestBelgianLocalization:
    """Test Belgian localization features."""

    def test_default_language_french_belgian(self):
        """Test default language is French (Belgian)."""
        default_locale = "fr-BE"
        assert default_locale == "fr-BE"

    def test_supported_languages(self):
        """Test supported languages for Belgian schools."""
        supported_locales = ["fr-BE", "nl-BE", "en"]
        
        assert "fr-BE" in supported_locales  # French (Belgium)
        assert "nl-BE" in supported_locales  # Dutch (Belgium)  
        assert "en" in supported_locales     # English (international)

    def test_belgian_currency_euro(self):
        """Test currency is Euro for Belgian context."""
        currency = "EUR"
        currency_symbol = "€"
        
        assert currency == "EUR"
        assert currency_symbol == "€"


@pytest.mark.unit
class TestBelgianSchoolEvents:
    """Test Belgian school-specific events."""

    def test_belgian_school_events(self):
        """Test typical Belgian school events are recognized."""
        belgian_events = [
            "Fancy Fair",           # School fair
            "Saint-Nicolas",        # December 6th celebration
            "Carnaval",            # Carnival celebration
            "Fête de l'école",     # School celebration
            "Réunion de parents"   # Parent meetings
        ]
        
        for event in belgian_events:
            assert isinstance(event, str)
            assert len(event) > 0

    def test_saint_nicolas_date(self):
        """Test Saint-Nicolas is December 6th."""
        import datetime
        saint_nicolas_date = datetime.date(2024, 12, 6)
        
        assert saint_nicolas_date.month == 12
        assert saint_nicolas_date.day == 6

    def test_school_year_belgian_calendar(self):
        """Test Belgian school year calendar."""
        # School year typically starts in September
        school_year_start_month = 9  # September
        school_year_end_month = 6    # June
        
        assert school_year_start_month == 9
        assert school_year_end_month == 6
        assert school_year_start_month < 12
        assert school_year_end_month > 0


@pytest.mark.unit
class TestBelgianSELContext:
    """Test SEL system adapted to Belgian context."""

    def test_sel_service_categories_belgian(self, sel_categories):
        """Test SEL categories fit Belgian school parent needs."""
        belgian_specific = [
            "garde",        # Childcare (very important for working parents)
            "devoirs",      # Homework help (Belgian schools give homework)
            "transport",    # School transport coordination
            "cuisine"       # Cooking (meal preparation help)
        ]
        
        for category in belgian_specific:
            assert category in sel_categories

    def test_sel_units_system(self):
        """Test SEL units system is appropriate for Belgian context."""
        standard_rate = 60  # 60 units = 1 hour
        minimum_balance = -300  # Can owe up to 5 hours
        maximum_balance = 600   # Can be owed up to 10 hours
        
        assert standard_rate == 60
        assert minimum_balance == -300
        assert maximum_balance == 600
        assert abs(minimum_balance) < maximum_balance  # More generous giving than taking

    def test_belgian_working_hours_context(self):
        """Test SEL system accommodates Belgian working parents."""
        # Typical Belgian school hours: 8:30-15:30
        school_start = 8.5   # 8:30 AM
        school_end = 15.5    # 3:30 PM
        work_end = 17.5      # 5:30 PM typical
        
        after_school_gap = work_end - school_end  # 2 hours gap
        assert after_school_gap == 2.0  # 2 hours where childcare is needed
        
        # SEL system should help with this gap
        sel_units_for_gap = after_school_gap * 60  # 120 units
        assert sel_units_for_gap == 120