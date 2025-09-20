# Makefile Integration Tests
"""
Tests that verify the Makefile commands work correctly with the test suite.
These tests ensure the new testing infrastructure integrates well with the existing Makefile.
"""

import os
import subprocess
from pathlib import Path

import pytest


class TestMakefileTestIntegration:
    """Test that Makefile test commands work correctly."""

    def test_makefile_test_command_exists(self):
        """Test that make test command is defined."""
        # Check if make test is defined in Makefile
        repo_root = Path(__file__).resolve().parents[3]
        result = subprocess.run(["make", "help"], capture_output=True, text=True, cwd=str(repo_root))

        assert result.returncode == 0
        assert "test" in result.stdout

    def test_pytest_dependencies_installable(self):
        """Test that test dependencies can be installed."""
        repo_root = Path(__file__).resolve().parents[3]
        requirements_file = str(repo_root / "backend/requirements.test.txt")
        assert os.path.exists(requirements_file)

        # Verify file has pytest dependencies
        with open(requirements_file, "r") as f:
            content = f.read()
            assert "pytest" in content
            assert "pytest-asyncio" in content
            assert "pytest-cov" in content

    def test_pytest_configuration(self):
        """Test pytest.ini configuration is valid."""
        repo_root = Path(__file__).resolve().parents[3]
        pytest_ini = str(repo_root / "backend/pytest.ini")
        assert os.path.exists(pytest_ini)

        with open(pytest_ini, "r") as f:
            content = f.read()
            assert "testpaths = tests" in content
            assert "--cov=app" in content
            assert "DATABASE_URL = sqlite:///test.db" in content

    def test_test_directory_structure(self):
        """Test that test directory structure is correct."""
        repo_root = Path(__file__).resolve().parents[3]
        base_dir = str(repo_root / "backend/tests")

        # Main directories should exist
        assert os.path.exists(f"{base_dir}")
        assert os.path.exists(f"{base_dir}/unit")
        assert os.path.exists(f"{base_dir}/integration")

        # __init__.py files should exist
        assert os.path.exists(f"{base_dir}/__init__.py")
        assert os.path.exists(f"{base_dir}/unit/__init__.py")
        assert os.path.exists(f"{base_dir}/integration/__init__.py")

    def test_conftest_fixture_availability(self):
        """Test that conftest.py provides necessary fixtures."""
        repo_root = Path(__file__).resolve().parents[3]
        conftest_file = str(repo_root / "backend/tests/conftest.py")
        assert os.path.exists(conftest_file)

        with open(conftest_file, "r") as f:
            content = f.read()

            # Key fixtures should be defined
            assert "def db_session" in content
            assert "def client" in content
            assert "def test_user_parent" in content
            assert "def auth_headers_parent" in content

    def test_test_files_exist_and_valid(self):
        """Test that test files exist and have valid Python syntax."""
        repo_root = Path(__file__).resolve().parents[3]
        test_files = [
            str(repo_root / "backend/tests/unit/test_auth.py"),
            str(repo_root / "backend/tests/unit/test_sel_system.py"),
            str(repo_root / "backend/tests/unit/test_belgian_context.py"),
            str(repo_root / "backend/tests/integration/test_api_complete_flows.py"),
            str(repo_root / "backend/tests/integration/test_database_operations.py"),
        ]

        for test_file in test_files:
            assert os.path.exists(test_file), f"Test file {test_file} should exist"

            # Check if file compiles (basic syntax check)
            with open(test_file, "r") as f:
                content = f.read()
                compile(content, test_file, "exec")  # Will raise if syntax error

    def test_markers_properly_defined(self):
        """Test that pytest markers are properly defined."""
        repo_root = Path(__file__).resolve().parents[3]
        pytest_ini = str(repo_root / "backend/pytest.ini")

        with open(pytest_ini, "r") as f:
            content = f.read()

            # Check marker definitions
            assert "unit:" in content
            assert "integration:" in content
            assert "auth:" in content
            assert "sel:" in content


class TestTestCoverage:
    """Test that test coverage is comprehensive."""

    def test_auth_tests_cover_main_scenarios(self):
        """Test that authentication tests cover main scenarios."""
        repo_root = Path(__file__).resolve().parents[3]
        auth_test_file = str(repo_root / "backend/tests/unit/test_auth.py")

        with open(auth_test_file, "r") as f:
            content = f.read()

            # Key test scenarios should be covered
            assert "test_register_new_user" in content
            assert "test_login_valid_credentials" in content
            assert "test_login_invalid_password" in content
            assert "test_get_current_user" in content

    def test_sel_tests_cover_belgian_context(self):
        """Test that SEL tests cover Belgian-specific requirements."""
        repo_root = Path(__file__).resolve().parents[3]
        sel_test_file = str(repo_root / "backend/tests/unit/test_sel_system.py")

        with open(sel_test_file, "r") as f:
            content = f.read()

            # Belgian SEL rules should be tested
            assert "120" in content  # Initial balance
            assert "-300" in content  # Minimum balance
            assert "600" in content  # Maximum balance
            assert "belgian" in content.lower()

    def test_belgian_context_tests_comprehensive(self):
        """Test that Belgian context tests are comprehensive."""
        repo_root = Path(__file__).resolve().parents[3]
        belgian_test_file = str(repo_root / "backend/tests/unit/test_belgian_context.py")

        with open(belgian_test_file, "r") as f:
            content = f.read()

            # Belgian school system should be covered
            assert "M1" in content and "M3" in content  # Maternelle
            assert "P1" in content and "P6" in content  # Primaire
            assert "CEB" in content  # P6 certification
            assert "fr-BE" in content  # Belgian French
            assert "nl-BE" in content  # Belgian Dutch

    def test_integration_tests_cover_complete_flows(self):
        """Test that integration tests cover complete user flows."""
        repo_root = Path(__file__).resolve().parents[3]
        integration_test_file = str(
            repo_root / "backend/tests/integration/test_api_complete_flows.py"
        )

        with open(integration_test_file, "r") as f:
            content = f.read()

            # Complete flows should be tested
            assert "test_complete_parent_onboarding_flow" in content
            assert "test_complete_sel_transaction_flow" in content
            assert "register" in content and "login" in content and "service" in content


if __name__ == "__main__":
    # This allows running the test file directly for debugging
    pytest.main([__file__])
