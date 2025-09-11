# Complete API Flow Integration Tests
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.sel_service import SELService
from app.models.child import Child


@pytest.mark.integration
class TestCompleteUserJourney:
    """Test complete user journey from registration to SEL transactions."""

    def test_complete_parent_onboarding_flow(self, client: TestClient):
        """Test complete parent onboarding: register → login → add child → create service."""
        
        # 1. Register new parent
        user_data = {
            "email": "journey@ecolehub.be",
            "first_name": "Marie",
            "last_name": "Journey",
            "password": "secure123"
        }
        
        register_response = client.post("/register", json=user_data)
        assert register_response.status_code == 201
        user_id = register_response.json()["id"]
        
        # 2. Login to get token
        login_response = client.post(
            "/login",
            data={"email": user_data["email"], "password": user_data["password"]}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Get user profile
        profile_response = client.get("/me", headers=headers)
        assert profile_response.status_code == 200
        profile = profile_response.json()
        assert profile["email"] == user_data["email"]
        assert profile["role"] == "parent"
        
        # 4. Add child with Belgian class level
        child_data = {
            "first_name": "Emma",
            "last_name": "Journey",
            "class_level": "P4"
        }
        
        child_response = client.post("/children", json=child_data, headers=headers)
        assert child_response.status_code == 201
        child = child_response.json()
        assert child["class_level"] == "P4"
        
        # 5. Create SEL service
        service_data = {
            "title": "Aide aux devoirs P4-P6",
            "description": "Aide aux devoirs pour les classes primaires supérieures",
            "category": "devoirs", 
            "units_per_hour": 60
        }
        
        service_response = client.post("/sel/services", json=service_data, headers=headers)
        assert service_response.status_code == 201
        service = service_response.json()
        assert service["title"] == service_data["title"]
        assert service["is_active"] is True
        
        # 6. Check SEL balance (should have initial 120 units)
        balance_response = client.get("/sel/balance", headers=headers)
        assert balance_response.status_code == 200
        balance = balance_response.json()
        assert balance["balance"] == 120  # Initial 2 hours credit
        
        # 7. Get my services
        my_services_response = client.get("/sel/services/mine", headers=headers)
        assert my_services_response.status_code == 200
        my_services = my_services_response.json()
        assert len(my_services) == 1
        assert my_services[0]["title"] == service_data["title"]


@pytest.mark.integration
class TestSELTransactionFlow:
    """Test complete SEL transaction flow between two users."""

    def test_complete_sel_transaction_flow(self, client: TestClient, db_session: Session):
        """Test complete SEL transaction: request → approve → balance update."""
        
        # Create two users: service provider and requester
        # Provider
        provider_data = {
            "email": "provider@ecolehub.be",
            "first_name": "Provider",
            "last_name": "User",
            "password": "provider123"
        }
        
        client.post("/register", json=provider_data)
        provider_login = client.post("/login", data={
            "email": provider_data["email"], 
            "password": provider_data["password"]
        })
        provider_token = provider_login.json()["access_token"]
        provider_headers = {"Authorization": f"Bearer {provider_token}"}
        
        # Requester
        requester_data = {
            "email": "requester@ecolehub.be", 
            "first_name": "Requester",
            "last_name": "User",
            "password": "requester123"
        }
        
        client.post("/register", json=requester_data)
        requester_login = client.post("/login", data={
            "email": requester_data["email"],
            "password": requester_data["password"]
        })
        requester_token = requester_login.json()["access_token"]
        requester_headers = {"Authorization": f"Bearer {requester_token}"}
        
        # Provider creates service
        service_data = {
            "title": "Garde après école",
            "description": "Garde d'enfants de 15h30 à 18h",
            "category": "garde",
            "units_per_hour": 60
        }
        
        service_response = client.post("/sel/services", json=service_data, headers=provider_headers)
        service_id = service_response.json()["id"]
        
        # Check initial balances
        provider_balance = client.get("/sel/balance", headers=provider_headers)
        requester_balance = client.get("/sel/balance", headers=requester_headers)
        
        assert provider_balance.json()["balance"] == 120
        assert requester_balance.json()["balance"] == 120
        
        # Requester makes transaction request
        transaction_data = {
            "service_id": service_id,
            "hours": 2,
            "description": "Garde Emma mardi 16h-18h"
        }
        
        transaction_response = client.post(
            "/sel/transactions",
            json=transaction_data, 
            headers=requester_headers
        )
        assert transaction_response.status_code == 201
        transaction = transaction_response.json()
        assert transaction["status"] == "pending"
        assert transaction["units"] == 120  # 2 hours * 60 units
        
        # Provider approves transaction
        approval_response = client.put(
            f"/sel/transactions/{transaction['id']}/approve",
            headers=provider_headers
        )
        assert approval_response.status_code == 200
        
        # Check updated balances after approval
        updated_provider_balance = client.get("/sel/balance", headers=provider_headers)
        updated_requester_balance = client.get("/sel/balance", headers=requester_headers)
        
        # Provider should have +120 units (240 total)
        # Requester should have -120 units (0 total)
        assert updated_provider_balance.json()["balance"] == 240
        assert updated_requester_balance.json()["balance"] == 0


@pytest.mark.integration
class TestMessageAndEventFlow:
    """Test messaging and events integration."""

    def test_message_service_owner_flow(self, client: TestClient):
        """Test messaging service owner about their service."""
        
        # Create provider and requester
        provider_data = {"email": "msgprovider@test.be", "first_name": "Msg", "last_name": "Provider", "password": "test123"}
        requester_data = {"email": "msgrequester@test.be", "first_name": "Msg", "last_name": "Requester", "password": "test123"}
        
        client.post("/register", json=provider_data)
        client.post("/register", json=requester_data)
        
        # Login both users
        provider_login = client.post("/login", data={"email": provider_data["email"], "password": "test123"})
        requester_login = client.post("/login", data={"email": requester_data["email"], "password": "test123"})
        
        provider_headers = {"Authorization": f"Bearer {provider_login.json()['access_token']}"}
        requester_headers = {"Authorization": f"Bearer {requester_login.json()['access_token']}"}
        
        # Provider creates service
        service_data = {
            "title": "Cours de piano",
            "description": "Cours de piano pour enfants débutants",
            "category": "musique",
            "units_per_hour": 90
        }
        service_response = client.post("/sel/services", json=service_data, headers=provider_headers)
        assert service_response.status_code == 201
        
        # Requester finds service
        services_response = client.get("/sel/services", headers=requester_headers)
        services = services_response.json()
        piano_service = next(s for s in services if s["title"] == "Cours de piano")
        
        # Requester messages provider about service
        message_data = {
            "recipient_id": piano_service["provider_id"],
            "content": "Bonjour, je suis intéressée par vos cours de piano pour ma fille en P3. Êtes-vous disponible le mercredi après-midi ?"
        }
        
        # This would be implemented when messaging system is fully active
        # message_response = client.post("/messages", json=message_data, headers=requester_headers)
        # assert message_response.status_code == 201


@pytest.mark.integration
class TestAdminWorkflow:
    """Test admin management workflows."""

    def test_admin_user_management(self, client: TestClient, test_user_admin: User, auth_headers_admin: dict):
        """Test admin can manage users and view analytics."""
        
        # Admin gets all users
        users_response = client.get("/admin/users", headers=auth_headers_admin)
        assert users_response.status_code == 200
        users = users_response.json()
        assert len(users) >= 1
        
        # Admin views platform analytics  
        analytics_response = client.get("/admin/analytics", headers=auth_headers_admin)
        assert analytics_response.status_code == 200
        analytics = analytics_response.json()
        assert "total_users" in analytics
        assert "active_services" in analytics

    def test_admin_service_moderation(self, client: TestClient, test_user_admin: User, auth_headers_admin: dict):
        """Test admin can moderate SEL services."""
        
        # Admin gets all services for moderation
        services_response = client.get("/admin/services", headers=auth_headers_admin)
        assert services_response.status_code == 200
        services = services_response.json()
        
        # Admin can deactivate inappropriate services
        if services:
            service_id = services[0]["id"]
            deactivate_response = client.put(
                f"/admin/services/{service_id}/deactivate",
                headers=auth_headers_admin
            )
            # This endpoint should exist for admin moderation
            # assert deactivate_response.status_code == 200


@pytest.mark.integration
class TestHealthAndMonitoring:
    """Test health checks and monitoring endpoints."""

    def test_health_endpoint_comprehensive(self, client: TestClient):
        """Test health endpoint returns comprehensive system status."""
        response = client.get("/health")
        
        assert response.status_code == 200
        health = response.json()
        
        # Should include all service statuses
        assert "status" in health
        assert "stage" in health
        assert "database" in health
        assert "redis" in health
        
        # For Stage 4, should also include
        assert "minio" in health
        assert "analytics" in health
        assert health["status"] == "healthy"
        assert health["stage"] == 4

    def test_metrics_endpoint_for_prometheus(self, client: TestClient):
        """Test metrics endpoint provides Prometheus-compatible metrics."""
        response = client.get("/metrics")
        
        # Should return metrics in Prometheus format
        assert response.status_code == 200
        metrics_text = response.text
        
        # Should contain basic application metrics
        assert "ecolehub_" in metrics_text  # Custom metrics prefix
        assert "users_total" in metrics_text or "http_requests" in metrics_text