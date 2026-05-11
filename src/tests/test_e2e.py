"""
E2E TESTS — Наскрізні сценарії
================================
Симулюємо реальні сценарії користувача від початку до кінця.
Кожен тест — повна послідовність дій як реальний користувач.
"""
import pytest


class TestE2E_FullRentFlow:
    """
    E2E: Повний цикл оренди квартири.
    Клієнт реєструється → власник створює оголошення →
    клієнт переглядає → додає в улюблені → залишає відгук → оформлює договір.
    """

    def test_full_rent_scenario(self, client):
        
        owner_resp = client.post("/api/users/", json={
            "name": "Петро",
            "surname": "Власник",
            "email": "owner_e2e@example.com",
            "phone_number": "0671111111",
            "id_card_series": "ОВ000001",
            "role": "client",  # спочатку client
            "password": "ownerpass"
        })
        assert owner_resp.status_code == 201
        assert owner_resp.json()["role"] == "client"

        owner_token = client.post("/api/auth/login", data={
            "username": "owner_e2e@example.com",
            "password": "ownerpass"
        }).json()["access_token"]
        owner_headers = {"Authorization": f"Bearer {owner_token}"}

        
        tenant_resp = client.post("/api/users/", json={
            "name": "Олена",
            "surname": "Орендар",
            "email": "tenant_e2e@example.com",
            "phone_number": "0672222222",
            "id_card_series": "ОО000002",
            "role": "client",
            "password": "tenantpass"
        })
        assert tenant_resp.status_code == 201
        tenant_id = tenant_resp.json()["id"]

        tenant_token = client.post("/api/auth/login", data={
            "username": "tenant_e2e@example.com",
            "password": "tenantpass"
        }).json()["access_token"]
        tenant_headers = {"Authorization": f"Bearer {tenant_token}"}

     
        addr_resp = client.post("/api/addresses/", json={
            "street": "вул. Хрещатик",
            "building": "10",
            "apartment_number": "5"
        }, headers=owner_headers)
        assert addr_resp.status_code == 200
        addr_id = addr_resp.json()["id"]

       
        apt_resp = client.post("/api/apartments/", json={
            "title": "Квартира в центрі Києва",
            "description": "Є газова плита, індивідуальне опалення, укриття поблизу",
            "city": "Київ",
            "type": "Квартира",
            "area": 55.0,
            "price": 7000,
            "room_count": 2,
            "address_id": addr_id,
            "telegram": "@petro_owner"
        }, headers=owner_headers)
        assert apt_resp.status_code == 201
        apt_id = apt_resp.json()["id"]
        owner_id = apt_resp.json()["owner_id"]

       
        me = client.get("/api/auth/me", headers=owner_headers).json()
        assert me["role"] == "owner"

       
        details = client.get(f"/api/apartments/listing/{apt_id}").json()
        assert details["title"] == "Квартира в центрі Києва"
        assert details["telegram"] == "@petro_owner"
        assert details["owner"]["phone_number"] == "0671111111"

        
        fav_resp = client.post(f"/api/apartments/favorites/{apt_id}",
                               headers=tenant_headers)
        assert fav_resp.status_code==200

        favorites = client.get("/api/apartments/favorites",
                               headers=tenant_headers).json()
        assert any(a["id"]==apt_id for a in favorites)

       
        review_resp = client.post(f"/api/reviews/{apt_id}", json={"text": "Чудова квартира, газова плита є!"},headers=tenant_headers)
        assert review_resp.status_code == 201
        assert review_resp.json()["author_name"] == "Олена"

        
        reviews = client.get(f"/api/reviews/{apt_id}").json()
        assert len(reviews) == 1

       
        contract_resp = client.post("/api/contracts/", json={
            "apartment_id": apt_id,
            "owner_id":owner_id,
            "client_id":tenant_id,
            "start_date":"2026-07-01",
            "end_date":"2026-08-01",
            "price":7000.0,
            "total_sum":    7000.0
        }, headers=tenant_headers)
        assert contract_resp.status_code in (200, 201)

        # ── Крок 9: Орендар бачить свої контракти ────────────────────
        contracts = client.get("/api/contracts/my-contracts",
                               headers=tenant_headers).json()
        assert isinstance(contracts, list)

        # ── Крок 10: Власник видаляє оголошення ──────────────────────
        del_resp = client.delete(f"/api/apartments/{apt_id}",
                                 headers=owner_headers)
        assert del_resp.status_code == 204

        # Роль повернулась до client (останнє оголошення видалено)
        me_after = client.get("/api/auth/me", headers=owner_headers).json()
        assert me_after["role"] == "client"


class TestE2E_SearchAndFilter:
    """E2E: Пошук і фільтрація оголошень."""

    def test_search_flow(self, client, auth_headers, sample_address):
        """Створюємо кілька квартир і перевіряємо фільтри."""
        # Створюємо 3 оголошення
        apts_data = [
            {"title": "Київська з газом", "city": "Київ",
             "description": "газова плита, паркінг", "price": 5000, "type": "Квартира"},
            {"title": "Львівська з укриттям", "city": "Львів",
             "description": "укриття поблизу, тихий район", "price": 4000, "type": "Будинок"},
            {"title": "Київська студія", "city": "Київ",
             "description": "студія в центрі", "price": 3000, "type": "Студія"},
        ]
        created = []
        for data in apts_data:
            resp = client.post("/api/apartments/", json={
                **data,
                "area": 40.0, "room_count": 1,
                "address_id": sample_address["id"]
            }, headers=auth_headers)
            assert resp.status_code == 201
            created.append(resp.json())

        # Активуємо оголошення через patch (статус active)
        for apt in created:
            client.patch(f"/api/apartments/{apt['id']}",
                         json={"status": "active"},
                         headers=auth_headers)

        # Перевіряємо загальний список
        all_resp = client.get("/api/apartments/").json()
        assert len(all_resp) >= 3

        # Перевіряємо my-listings
        my = client.get("/api/apartments/my-listings", headers=auth_headers).json()
        assert len(my) == 3


class TestE2E_AdminFlow:
    """E2E: Адміністративний сценарій."""

    def test_admin_can_delete_any_apartment(self, client, admin_headers,
                                            sample_apartment):
        """Адмін може видалити будь-яке оголошення."""
        apt_id = sample_apartment["id"]
        resp = client.delete(f"/api/apartments/{apt_id}", headers=admin_headers)
        assert resp.status_code == 204

    def test_admin_can_delete_any_review(self, client, admin_headers, sample_apartment):
        """Адмін може видалити будь-який відгук."""
        # Спочатку додаємо відгук від звичайного користувача
        client.post("/api/users/", json={
            "name": "Авт",
            "surname": "Відгук",
            "email": "reviewer2@example.com",
            "phone_number": "0993334455",
            "id_card_series": "АВ999999",
            "role": "client",
            "password": "pass"
        })
        rev_token = client.post("/api/auth/login", data={
            "username": "reviewer2@example.com", "password": "pass"
        }).json()["access_token"]
        rev_headers = {"Authorization": f"Bearer {rev_token}"}

        apt_id = sample_apartment["id"]
        review = client.post(f"/api/reviews/{apt_id}",
                             json={"text": "Відгук для видалення"},
                             headers=rev_headers).json()

        # Адмін видаляє
        del_resp = client.delete(f"/api/reviews/{review['id']}",
                                 headers=admin_headers)
        assert del_resp.status_code == 204
