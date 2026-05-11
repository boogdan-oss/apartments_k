"""
conftest.py — спільні фікстури для всіх тестів.
"""
import sys
import os

# ✅ КРОК 1: встановлюємо змінні середовища ДО будь-яких імпортів
# Щоб config.py не падав з ValidationError
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test_secret_key_for_testing_only")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

# ✅ КРОК 2: додаємо src/ до шляху — щоб знайти main.py, routers, models і т.д.
# tests/ знаходиться в src/tests/, тому піднімаємось на один рівень вгору
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SRC_DIR)

# ✅ Тепер можна імпортувати
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db
import models

# -------------------------------------------------------
# Тестова БД — SQLite в пам'яті, не чіпає реальну PostgreSQL
# -------------------------------------------------------
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Створює таблиці перед кожним тестом і видаляє після."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def registered_client(client):
    resp = client.post("/api/users/", json={
        "name": "Іван",
        "surname": "Тест",
        "email": "test_client@example.com",
        "phone_number": "0991112233",
        "id_card_series": "АВ123456",
        "date_of_birth": "1995-05-15",
        "role": "client",
        "password": "testpassword123"
    })
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture
def auth_token(client, registered_client):
    resp = client.post("/api/auth/login", data={
        "username": "test_client@example.com",
        "password": "testpassword123"
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def registered_admin(client):
    resp = client.post("/api/users/", json={
        "name": "Адмін",
        "surname": "Тест",
        "email": "admin@example.com",
        "phone_number": "0990000000",
        "id_card_series": "АД000001",
        "role": "admin",
        "password": "adminpass123"
    })
    return resp.json()


@pytest.fixture
def admin_token(client, registered_admin):
    resp = client.post("/api/auth/login", data={
        "username": "admin@example.com",
        "password": "adminpass123"
    })
    return resp.json()["access_token"]


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def sample_address(client, auth_headers):
    resp = client.post("/api/addresses/", json={
        "street": "вул. Тестова",
        "building": "1",
        "apartment_number": "1"
    }, headers=auth_headers)
    assert resp.status_code == 200
    return resp.json()


@pytest.fixture
def sample_apartment(client, auth_headers, sample_address):
    resp = client.post("/api/apartments/", json={
        "title": "Тестова квартира",
        "description": "Опис тестової квартири з газовою плитою",
        "city": "Київ",
        "type": "Квартира",
        "area": 50.0,
        "price": 5000,
        "room_count": 2,
        "address_id": sample_address["id"],
        "telegram": "@test_owner"
    }, headers=auth_headers)
    assert resp.status_code == 201
    return resp.json()