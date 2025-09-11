# Simple test to verify basic functionality
def test_simple():
    """Test that basic testing works."""
    assert 1 + 1 == 2

def test_ecolehub_stage():
    """Test Stage 4 configuration."""
    import os
    stage = os.environ.get("STAGE", "0")
    assert stage in ["4", "0"]  # Either set to 4 or default 0