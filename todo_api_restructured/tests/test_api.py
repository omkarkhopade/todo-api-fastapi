from app.models.user import UserRole
from tests.conftest import auth_headers


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_login_and_protected_route(client, db_session):
    response = client.post(
        "/api/auth/register",
        json={"email": "USER@Example.com", "password": "strong-password"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "user@example.com"
    assert response.json()["role"] == UserRole.USER.value

    headers = auth_headers(client, "user@example.com", "strong-password")
    response = client.get("/api/user/tasks", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


def test_registration_cannot_select_admin_role(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "attacker@example.com",
            "password": "strong-password",
            "role": "ADMIN",
        },
    )
    assert response.status_code == 422


def test_admin_task_workflow(client, db_session, admin):
    client.post(
        "/api/auth/register",
        json={"email": "worker@example.com", "password": "worker-password"},
    )
    worker_headers = auth_headers(client, "worker@example.com", "worker-password")
    admin_headers = auth_headers(client, "admin@example.com", "admin-password")

    worker = db_session.query(type(admin)).filter_by(email="worker@example.com").one()
    response = client.post(
        "/api/admin/tasks",
        headers=admin_headers,
        json={"assigned_to_id": worker.id, "name": "Ship release", "priority": "high"},
    )
    assert response.status_code == 201
    task_id = response.json()["id"]

    response = client.put(f"/api/user/tasks/{task_id}/complete", headers=worker_headers)
    assert response.status_code == 200

    response = client.get(f"/api/user/tasks/{task_id}", headers=worker_headers)
    assert response.json()["status"] == "completed"

    response = client.delete(f"/api/admin/tasks/{task_id}", headers=admin_headers)
    assert response.status_code == 204


def test_authentication_is_required(client):
    response = client.get("/api/user/tasks")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
