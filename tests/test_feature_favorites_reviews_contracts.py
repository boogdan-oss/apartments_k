"""
FEATURE TESTS — Улюблені, Відгуки, Контракти
==============================================
"""
import pytest


class TestFavorites:
    """Фіча: Додавання/видалення улюблених."""

    def test_add_to_favorites(self, client, auth_headers, sample_apartment):
        apt_id = sample_apartment["id"]
        resp = client.post(f"/api/apartments/favorites/{apt_id}",
                           headers=auth_headers)
        assert resp.status_code == 200
        assert "Додано" in resp.json()["message"]

    def test_add_duplicate_favorite(self, client, auth_headers, sample_apartment):
        """Повторне додавання — повідомлення що вже є."""
        apt_id = sample_apartment["id"]
        client.post(f"/api/apartments/favorites/{apt_id}", headers=auth_headers)
        resp = client.post(f"/api/apartments/favorites/{apt_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert "Вже" in resp.json()["message"]

    def test_get_favorites(self, client, auth_headers, sample_apartment):
        """Список улюблених повертає квартири."""
        apt_id = sample_apartment["id"]
        client.post(f"/api/apartments/favorites/{apt_id}", headers=auth_headers)
        resp = client.get("/api/apartments/favorites", headers=auth_headers)
        assert resp.status_code == 200
        ids = [a["id"] for a in resp.json()]
        assert apt_id in ids

    def test_remove_from_favorites(self, client, auth_headers, sample_apartment):
        apt_id = sample_apartment["id"]
        client.post(f"/api/apartments/favorites/{apt_id}", headers=auth_headers)
        resp = client.delete(f"/api/apartments/favorites/{apt_id}",
                             headers=auth_headers)
        assert resp.status_code == 200
        assert "Видалено" in resp.json()["message"]

    def test_remove_nonexistent_favorite(self, client, auth_headers, sample_apartment):
        """Видалення того чого немає — 404."""
        resp = client.delete(f"/api/apartments/favorites/{sample_apartment['id']}",
                             headers=auth_headers)
        assert resp.status_code == 404


class TestReviews:
    """Фіча: Відгуки під оголошеннями."""

    def _second_user_headers(self, client):
        """Другий користувач для написання відгуку."""
        client.post("/api/users/", json={
            "name": "Рецензент",
            "surname": "Тест",
            "email": "reviewer@example.com",
            "phone_number": "0665554433",
            "id_card_series": "РЦ000001",
            "role": "client",
            "password": "reviewpass"
        })
        token = client.post("/api/auth/login", data={
            "username": "reviewer@example.com",
            "password": "reviewpass"
        }).json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_add_review(self, client, sample_apartment):
        """Інший користувач може залишити відгук."""
        headers = self._second_user_headers(client)
        apt_id = sample_apartment["id"]
        resp = client.post(f"/api/reviews/{apt_id}",
                           json={"text": "Чудова квартира, рекомендую!"},
                           headers=headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["text"] == "Чудова квартира, рекомендую!"
        assert "author_name" in data
        assert "created_at" in data

    def test_owner_cannot_review_own_apartment(self, client, auth_headers,
                                               sample_apartment):
        """Власник не може писати відгук на своє оголошення."""
        apt_id = sample_apartment["id"]
        resp = client.post(f"/api/reviews/{apt_id}",
                           json={"text": "Сам себе хвалю"},
                           headers=auth_headers)
        assert resp.status_code == 403

    def test_get_reviews(self, client, sample_apartment):
        """Список відгуків повертається без авторизації."""
        apt_id = sample_apartment["id"]
        resp = client.get(f"/api/reviews/{apt_id}")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_delete_own_review(self, client, sample_apartment):
        """Автор може видалити свій відгук."""
        headers = self._second_user_headers(client)
        apt_id = sample_apartment["id"]

        create_resp = client.post(f"/api/reviews/{apt_id}",
                                  json={"text": "Тест видалення"},
                                  headers=headers)
        review_id = create_resp.json()["id"]

        del_resp = client.delete(f"/api/reviews/{review_id}", headers=headers)
        assert del_resp.status_code == 204


class TestContracts:
    """Фіча: Створення та управління контрактами."""

    def test_create_contract(self, client, auth_headers, registered_client,
                             sample_apartment):
        """Клієнт може створити контракт на квартиру."""
        apt = sample_apartment
        resp = client.post("/api/contracts/", json={
            "apartment_id": apt["id"],
            "owner_id":     apt["owner_id"],
            "client_id":    registered_client["id"],
            "start_date":   "2026-06-01",
            "end_date":     "2026-07-01",
            "price":        float(apt["price"]),
            "total_sum":    float(apt["price"])
        }, headers=auth_headers)
        # Очікуємо або 200 або FileResponse (200) з docx
        assert resp.status_code in (200, 201)

    def test_get_my_contracts(self, client, auth_headers):
        """Список контрактів повертається авторизованому користувачу."""
        resp = client.get("/api/contracts/my-contracts", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_contracts_require_auth(self, client):
        """Без токена — 401."""
        resp = client.get("/api/contracts/my-contracts")
        assert resp.status_code == 401
