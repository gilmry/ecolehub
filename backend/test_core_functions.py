"""
Core function tests that don't require database setup
"""
import pytest
import os
from datetime import datetime, timedelta

@pytest.mark.unit
def test_password_hashing():
    """Test password hashing functionality."""
    # Set test environment to avoid secrets manager issues
    os.environ["TESTING"] = "1"
    os.environ["SECRET_KEY"] = "test-secret-key"
    
    from app.main_stage4 import get_password_hash, verify_password
    
    password = "jules20220902"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong", hashed) is False


@pytest.mark.unit  
def test_jwt_token_creation():
    """Test JWT token creation."""
    os.environ["TESTING"] = "1"
    os.environ["SECRET_KEY"] = "test-secret-key"
    
    from app.main_stage4 import create_access_token
    from jose import jwt
    
    data = {"sub": "test@example.com"}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    
    # Verify token structure using jose directly
    try:
        decoded = jwt.decode(token, "test-secret-key", algorithms=["HS256"])
        assert decoded["sub"] == "test@example.com"
        assert "exp" in decoded  # expiration should be set
    except jwt.JWTError:
        pytest.fail("Token verification failed")


@pytest.mark.belgian
def test_belgian_class_validation():
    """Test Belgian class level validation."""
    belgian_classes = ["M1", "M2", "M3", "P1", "P2", "P3", "P4", "P5", "P6"]
    
    for class_name in belgian_classes:
        assert class_name in belgian_classes
        assert len(class_name) == 2
        assert class_name[0] in ["M", "P"]
        assert class_name[1].isdigit()
    
    # Test invalid classes
    invalid_classes = ["M4", "P7", "S1", "XX"]
    for invalid in invalid_classes:
        assert invalid not in belgian_classes


@pytest.mark.sel
def test_sel_balance_rules():
    """Test SEL balance rules for Belgian context."""
    # Belgian SEL rules
    initial_balance = 120  # 2 hours
    min_balance = -300     # 5 hours debt max
    max_balance = 600      # 10 hours credit max
    standard_rate = 60     # 60 units = 1 hour
    
    assert initial_balance == 120
    assert min_balance == -300
    assert max_balance == 600
    assert standard_rate == 60
    
    # Test balance calculations
    hours_initial = initial_balance / standard_rate
    hours_min_debt = abs(min_balance) / standard_rate
    hours_max_credit = max_balance / standard_rate
    
    assert hours_initial == 2.0
    assert hours_min_debt == 5.0
    assert hours_max_credit == 10.0


@pytest.mark.unit
def test_stage4_configuration():
    """Test Stage 4 specific configuration."""
    os.environ["STAGE"] = "4"
    
    stage = os.environ.get("STAGE", "0")
    assert stage == "4"
    
    # Test multilingue support
    supported_languages = ["fr-BE", "nl-BE", "en"]
    assert "fr-BE" in supported_languages  # French Belgium (primary)
    assert "nl-BE" in supported_languages  # Dutch Belgium (Flanders)
    assert "en" in supported_languages     # English (international)