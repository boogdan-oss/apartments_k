"""
FEATURE TESTS — Авторизація та реєстрація
==========================================
"""
import pytest


class TestRegistration:
    """Фіча: Реєстрація нового користувача."""

    def test_register_client_success(self, client):
        resp = client.post("/api/users/", json={
            "name": "Марія",
            "surname": "Коваль",
            "email": "maria@example.com",
            "phone_number": "0931234567",
            "id_card_series": "МК112233",
            "date_of_birth": "2000-01-01",
            "role": "client",
            "password": "securepass"
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "maria@example.com"
        assert data["role"] == "client"
        # Пароль не повертається у відповіді
        assert "password" not in data
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client, registered_client):
        """Дублікат email — 400."""
        resp = client.post("/api/users/", json={
            "name": "Дублікат",
            "surname": "Юзер",
            "email": "test_client@example.com",  # вже існує
            "phone_number": "0990000001",
            "id_card_series": "ДБ000001",
            "role": "client",
            "password": "pass123"
        })
        assert resp.status_code == 400

    def test_register_without_required_fields(self, client):
        """Відсутні обов'язкові поля — 422."""
        resp = client.post("/api/users/", json={
            "name": "Без пошти"
        })
        assert resp.status_code == 422


class TestLogin:
    """Фіча: Вхід в систему."""

    def test_login_success(self, client, registered_client):
        resp = client.post("/api/auth/login", data={
            "username": "test_client@example.com",
            "password": "testpassword123"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, registered_client):
        resp = client.post("/api/auth/login", data={
            "username": "test_client@example.com",
            "password": "wrongpassword"
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post("/api/auth/login", data={
            "username": "nobody@example.com",
            "password": "anypass"
        })
        assert resp.status_code == 401

    def test_get_current_user(self, client, auth_headers, registered_client):
        """Токен дає доступ до профілю."""
        resp = client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == "test_client@example.com"

    def test_get_current_user_invalid_token(self, client):
        """Невалідний токен — 401."""
        resp = client.get("/api/auth/me",
                          headers={"Authorization": "Bearer invalid.token.here"})
        assert resp.status_code == 401
