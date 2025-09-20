import os
import re
import subprocess
from pathlib import Path

import pytest


pytestmark = pytest.mark.gdpr


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def test_user_model_has_gdpr_fields():
    # The User model should provide fields to record privacy consent metadata
    from app.models_stage1 import User

    assert hasattr(User, "consent_version"), "User.consent_version missing"
    assert hasattr(User, "consented_at"), "User.consented_at missing"
    assert hasattr(User, "privacy_locale"), "User.privacy_locale missing"


def test_secrets_are_not_committed():
    # Ensure secrets directory/files are not tracked by Git
    root = repo_root()
    secrets_dir = root / "secrets"
    if not secrets_dir.exists():
        # No secrets directory present in repo — OK
        return
    # List tracked files under secrets
    result = subprocess.run(
        ["git", "ls-files", str(secrets_dir)], capture_output=True, text=True, cwd=str(root)
    )
    assert result.returncode == 0
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    assert tracked == [], f"Secrets should not be tracked: {tracked}"


def test_env_example_has_no_secrets():
    # .env.example should not contain real secrets/keys
    root = repo_root()
    env_example = root / ".env.example"
    assert env_example.exists(), ".env.example must exist"
    content = env_example.read_text(encoding="utf-8", errors="ignore")
    forbidden_patterns = [
        r"BEGIN [A-Z ]*PRIVATE KEY",  # PEM keys
        r"AKIA[0-9A-Z]{16}",  # AWS-style access key
        r"secret",  # generic secret mentions
    ]
    for pat in forbidden_patterns:
        assert re.search(pat, content, re.IGNORECASE) is None, f"Forbidden secret pattern found: {pat}"


def test_backend_uses_env_for_secret_key():
    # Verify backend reads SECRET_KEY from env/secrets manager
    root = repo_root()
    main_stage4 = (root / "backend/app/main_stage4.py").read_text(encoding="utf-8", errors="ignore")
    assert (
        "get_jwt_secret" in main_stage4 or 'os.getenv("SECRET_KEY"' in main_stage4
    ), "Backend must read SECRET_KEY from env/secrets"


def test_frontend_has_legal_privacy_links():
    # Frontend should reference legal/privacy info for users (static check)
    root = repo_root()
    index_html = root / "frontend/index.html"
    assert index_html.exists(), "frontend/index.html missing"
    content = index_html.read_text(encoding="utf-8", errors="ignore").lower()
    # Look for common legal/privacy cues
    assert any(k in content for k in ["rgpd", "privacy", "mentions", "données", "protection", "legal"]), (
        "Frontend should include legal/privacy cues (RGPD/mentions/données)"
    )


def test_privacy_policy_endpoint(client):
    # Verify privacy endpoint exposes version and locales
    resp = client.get("/api/privacy")
    assert resp.status_code == 200
    data = resp.json()
    assert "version" in data and "locales" in data


def test_data_export_and_delete_flow(client):
    # Register and login
    reg = client.post(
        "/api/register",
        json={
            "email": "gdpruser@test.be",
            "first_name": "GDPR",
            "last_name": "User",
            "password": "secret123",
        },
    )
    assert reg.status_code in (200, 201)
    login = client.post(
        "/api/login",
        data={"email": "gdpruser@test.be", "password": "secret123"},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Data export
    export = client.get("/api/me/data_export", headers=headers)
    assert export.status_code == 200
    data = export.json()
    assert "user" in data and "children" in data and "services" in data

    # Delete (erasure)
    delete = client.delete("/api/me", headers=headers)
    assert delete.status_code == 200
    # Re-login should still reject if password invalidated (optional but we check is_active flag via /api/me)
    me = client.get("/api/me", headers=headers)
    assert me.status_code == 200
    profile = me.json()
    # After deletion, user is inactive and anonymized
    assert profile["is_active"] is False
    assert profile["email"].startswith("deleted+")
