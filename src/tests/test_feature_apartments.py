"""
FEATURE TESTS — Оголошення квартир
===================================
Тестуємо повний цикл: створення, читання, оновлення, видалення.
Кожен тест — окрема фіча з точки зору бізнес-логіки.
"""
import pytest


class TestCreateApartment:
    """Фіча: Створення нового оголошення."""

    def test_create_apartment_success(self, client, auth_headers, sample_address):
        """Авторизований користувач може створити оголошення."""
        resp = client.post("/api/apartments/", json={
            "title": "Простора квартира",
            "description": "Хороший район",
            "city": "Київ",
            "type": "Квартира",
            "area": 65.0,
            "price": 8000,
            "room_count": 3,
            "address_id": sample_address["id"],
            "telegram": "@owner123"
        }, headers=auth_headers)

        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Простора квартира"
        assert data["city"] == "Київ"
        assert data["telegram"] == "@owner123"
        assert "owner_id" in data

    def test_create_apartment_sets_owner_role(self, client, auth_headers,
                                              registered_client, sample_address):
        """При створенні першого оголошення роль змінюється з client на owner."""
        # До створення — роль client
        assert registered_client["role"] == "client"

        client.post("/api/apartments/", json={
            "title": "Квартира власника",
            "description": "Опис",
            "city": "Львів",
            "type": "Студія",
            "area": 30.0,
            "price": 3000,
            "room_count": 1,
            "address_id": sample_address["id"],
        }, headers=auth_headers)

        # Після створення — роль owner
        me_resp = client.get("/api/auth/me", headers=auth_headers)
        assert me_resp.json()["role"] == "owner"

    def test_create_apartment_unauthorized(self, client, sample_address):
        """Без токена — 401."""
        resp = client.post("/api/apartments/", json={
            "title": "Квартира",
            "description": "Опис",
            "city": "Київ",
            "type": "Квартира",
            "area": 50.0,
            "price": 5000,
            "room_count": 2,
            "address_id": sample_address["id"],
        })
        assert resp.status_code == 401

    def test_create_apartment_telegram_saved(self, client, auth_headers,
                                             sample_apartment):
        """Telegram зберігається і повертається в деталях."""
        listing_id = sample_apartment["id"]
        resp = client.get(f"/api/apartments/listing/{listing_id}")
        assert resp.status_code == 200
        assert resp.json()["telegram"] == "@test_owner"


class TestReadApartments:
    """Фіча: Перегляд оголошень."""

    def test_get_all_active_apartments(self, client, sample_apartment):
        """Список містить тільки активні оголошення."""
        resp = client.get("/api/apartments/")
        assert resp.status_code == 200
        # sample_apartment має статус pending — не показується
        apartments = resp.json()
        assert isinstance(apartments, list)

    def test_get_apartment_details(self, client, sample_apartment):
        """Деталі оголошення містять дані власника і фото."""
        listing_id = sample_apartment["id"]
        resp = client.get(f"/api/apartments/listing/{listing_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == listing_id
        assert "owner" in data
        assert "name" in data["owner"]
        assert "phone_number" in data["owner"]
        assert "images" in data

    def test_get_nonexistent_apartment(self, client):
        """Неіснуюче оголошення — 404."""
        resp = client.get("/api/apartments/listing/99999")
        assert resp.status_code == 404

    def test_get_my_listings(self, client, auth_headers, sample_apartment):
        """Власник бачить свої оголошення."""
        resp = client.get("/api/apartments/my-listings", headers=auth_headers)
        assert resp.status_code == 200
        listings = resp.json()
        assert any(a["id"] == sample_apartment["id"] for a in listings)


class TestUpdateApartment:
    """Фіча: Редагування оголошення."""

    def test_owner_can_update(self, client, auth_headers, sample_apartment):
        """Власник може редагувати своє оголошення."""
        apt_id = sample_apartment["id"]
        resp = client.patch(f"/api/apartments/{apt_id}",
                            json={"price": 9000},
                            headers=auth_headers)
        assert resp.status_code == 200
        assert float(resp.json()["price"]) == 9000

    def test_other_user_cannot_update(self, client, sample_apartment):
        """Інший користувач не може редагувати чуже оголошення."""
        # Реєструємо іншого користувача
        client.post("/api/users/", json={
            "name": "Інший",
            "surname": "Юзер",
            "email": "other@example.com",
            "phone_number": "0997778899",
            "id_card_series": "ХХ999999",
            "role": "client",
            "password": "pass123"
        })
        token_resp = client.post("/api/auth/login", data={
            "username": "other@example.com",
            "password": "pass123"
        })
        other_headers = {"Authorization": f"Bearer {token_resp.json()['access_token']}"}

        apt_id = sample_apartment["id"]
        resp = client.patch(f"/api/apartments/{apt_id}",
                            json={"price": 1},
                            headers=other_headers)
        assert resp.status_code == 403


class TestDeleteApartment:
    """Фіча: Видалення оголошення."""

    def test_owner_can_delete(self, client, auth_headers, sample_apartment):
        """Власник може видалити своє оголошення."""
        apt_id = sample_apartment["id"]
        resp = client.delete(f"/api/apartments/{apt_id}", headers=auth_headers)
        assert resp.status_code == 204

    def test_delete_last_apartment_demotes_to_client(self, client, auth_headers,
                                                      sample_apartment):
        """Видалення останнього оголошення повертає роль client."""
        apt_id = sample_apartment["id"]
        client.delete(f"/api/apartments/{apt_id}", headers=auth_headers)

        me_resp = client.get("/api/auth/me", headers=auth_headers)
        assert me_resp.json()["role"] == "client"
