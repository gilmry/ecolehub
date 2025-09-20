# Stage 4 Endpoint Integration Tests (i18n, analytics, shop)
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_i18n_locales_available(client: TestClient):
    resp = client.get("/api/i18n/locales")
    assert resp.status_code == 200
    locales = resp.json()
    codes = [l["code"] for l in locales]
    assert "fr-BE" in codes and "nl-BE" in codes and "de-BE" in codes and "en" in codes


@pytest.mark.integration
def test_platform_analytics_admin_only(client: TestClient):
    # Register an admin-like user and login
    reg = client.post(
        "/api/register",
        json={
            "email": "admin@test.be",
            "first_name": "Admin",
            "last_name": "User",
            "password": "admin123",
        },
    )
    assert reg.status_code == 200

    login = client.post(
        "/api/login",
        data={"email": "admin@test.be", "password": "admin123"},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Access analytics overview (admin only)
    resp = client.get("/api/analytics/platform", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    # Validate structure from analytics_service
    assert (
        "users" in data and "sel" in data and "shop" in data and "communication" in data
    )
    assert "timestamp" in data


@pytest.mark.integration
def test_shop_admin_create_and_list_products(client: TestClient):
    # Register admin user and login
    client.post(
        "/api/register",
        json={
            "email": "shopadmin@test.be",
            "first_name": "Shop",
            "last_name": "Admin",
            "password": "shopadmin123",
        },
    )
    login = client.post(
        "/api/login",
        data={"email": "shopadmin@test.be", "password": "shopadmin123"},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    token = login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {token}"}

    # Create a shop product (admin-only endpoint)
    create = client.post(
        "/api/shop/products",
        json={
            "name": "T-shirt école",
            "description": "T-shirt coton EcoleHub",
            "base_price": 12.5,
            "category": "uniform",
            "min_quantity": 5,
        },
        headers=admin_headers,
    )
    assert create.status_code == 200
    created = create.json()
    assert created["name"] == "T-shirt école"
    assert created["price"] == pytest.approx(12.5)

    # List products as the same (authenticated) user
    listing = client.get("/api/shop/products", headers=admin_headers)
    assert listing.status_code == 200
    products = listing.json()
    assert any(p.get("name") == "T-shirt école" for p in products)
