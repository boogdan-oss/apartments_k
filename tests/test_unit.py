"""
UNIT TESTS — Малі ізольовані функції
======================================
Тестуємо окремі функції без HTTP запитів і БД.
"""
import pytest
from datetime import datetime, date
from decimal import Decimal


# -------------------------------------------------------
# Unit тести для логіки фільтрації (як на фронті)
# Винесені у чисті функції для тестування
# -------------------------------------------------------

def filter_by_city(listings: list, city: str) -> list:
    """Фільтр по місту — регістронезалежний."""
    if not city:
        return listings
    return [l for l in listings if city.lower() in (l.get("city") or "").lower()]


def filter_by_type(listings: list, type_: str) -> list:
    """Фільтр по типу житла."""
    if not type_ or type_ == "Будь-який тип":
        return listings
    return [l for l in listings if l.get("type") == type_]


def filter_by_price(listings: list, price_from=None, price_to=None) -> list:
    """Фільтр по ціні."""
    result = listings
    if price_from:
        result = [l for l in result if float(l.get("price", 0)) >= float(price_from)]
    if price_to:
        result = [l for l in result if float(l.get("price", 0)) <= float(price_to)]
    return result


def filter_by_description(listings: list, keyword: str) -> list:
    """Фільтр по ключовому слову в описі — регістронезалежний."""
    if not keyword:
        return listings
    kw = keyword.lower()
    return [
        l for l in listings
        if kw in (l.get("description") or "").lower()
    ]


def format_review_date(date_str: str) -> str:
    """Форматування дати відгуку — без року якщо поточний."""
    d = datetime.fromisoformat(date_str)
    now = datetime.now()
    months_uk = [
        "", "січня", "лютого", "березня", "квітня", "травня", "червня",
        "липня", "серпня", "вересня", "жовтня", "листопада", "грудня"
    ]
    if d.year == now.year:
        return f"{d.day} {months_uk[d.month]}"
    return f"{d.day} {months_uk[d.month]} {d.year}"


def calculate_total_sum(price_per_month: float, start_date: date, end_date: date) -> float:
    """Розрахунок суми контракту по кількості днів."""
    days = (end_date - start_date).days
    return round(days * (price_per_month / 30), 2)


# -------------------------------------------------------
# FIXTURES
# -------------------------------------------------------

@pytest.fixture
def sample_listings():
    return [
        {"id": 1, "city": "Київ",  "type": "Квартира", "price": 5000,
         "description": "Є газова плита та індивідуальне опалення"},
        {"id": 2, "city": "Львів", "type": "Будинок",  "price": 8000,
         "description": "Укриття поблизу, паркінг"},
        {"id": 3, "city": "Київ",  "type": "Студія",   "price": 3000,
         "description": "Затишна студія в центрі"},
        {"id": 4, "city": "Одеса", "type": "Квартира", "price": 12000,
         "description": "Вид на море, кондиціонер"},
    ]


# -------------------------------------------------------
# UNIT ТЕСТИ — Фільтр по місту
# -------------------------------------------------------

class TestCityFilter:

    def test_filter_exact_city(self, sample_listings):
        result = filter_by_city(sample_listings, "Київ")
        assert len(result) == 2
        assert all(r["city"] == "Київ" for r in result)

    def test_filter_case_insensitive(self, sample_listings):
        """Регістр не важливий."""
        result = filter_by_city(sample_listings, "київ")
        assert len(result) == 2

    def test_filter_partial_city(self, sample_listings):
        """Часткове співпадіння."""
        result = filter_by_city(sample_listings, "Льв")
        assert len(result) == 1
        assert result[0]["city"] == "Львів"

    def test_filter_empty_string_returns_all(self, sample_listings):
        """Порожній рядок — всі результати."""
        result = filter_by_city(sample_listings, "")
        assert len(result) == 4

    def test_filter_no_match(self, sample_listings):
        result = filter_by_city(sample_listings, "Харків")
        assert len(result) == 0


# -------------------------------------------------------
# UNIT ТЕСТИ — Фільтр по типу
# -------------------------------------------------------

class TestTypeFilter:

    def test_filter_by_type(self, sample_listings):
        result = filter_by_type(sample_listings, "Квартира")
        assert len(result) == 2

    def test_filter_any_type_returns_all(self, sample_listings):
        result = filter_by_type(sample_listings, "Будь-який тип")
        assert len(result) == 4

    def test_filter_empty_returns_all(self, sample_listings):
        result = filter_by_type(sample_listings, "")
        assert len(result) == 4


# -------------------------------------------------------
# UNIT ТЕСТИ — Фільтр по ціні
# -------------------------------------------------------

class TestPriceFilter:

    def test_filter_price_from(self, sample_listings):
        result = filter_by_price(sample_listings, price_from=5000)
        assert all(float(r["price"]) >= 5000 for r in result)
        assert len(result) == 3

    def test_filter_price_to(self, sample_listings):
        result = filter_by_price(sample_listings, price_to=5000)
        assert all(float(r["price"]) <= 5000 for r in result)
        assert len(result) == 2

    def test_filter_price_range(self, sample_listings):
        result = filter_by_price(sample_listings, price_from=4000, price_to=9000)
        assert len(result) == 2

    def test_filter_no_price_returns_all(self, sample_listings):
        result = filter_by_price(sample_listings)
        assert len(result) == 4


# -------------------------------------------------------
# UNIT ТЕСТИ — Фільтр по опису
# -------------------------------------------------------

class TestDescriptionFilter:

    def test_filter_by_keyword(self, sample_listings):
        result = filter_by_description(sample_listings, "газова плита")
        assert len(result) == 1
        assert result[0]["id"] == 1

    def test_filter_case_insensitive(self, sample_listings):
        result = filter_by_description(sample_listings, "УКРИТТЯ")
        assert len(result) == 1
        assert result[0]["id"] == 2

    def test_filter_partial_word(self, sample_listings):
        result = filter_by_description(sample_listings, "паркінг")
        assert len(result) == 1

    def test_filter_empty_returns_all(self, sample_listings):
        result = filter_by_description(sample_listings, "")
        assert len(result) == 4

    def test_filter_no_match(self, sample_listings):
        result = filter_by_description(sample_listings, "басейн")
        assert len(result) == 0

    def test_combined_filters(self, sample_listings):
        """Комбінація фільтрів: місто + опис."""
        by_city = filter_by_city(sample_listings, "Київ")
        result  = filter_by_description(by_city, "газова")
        assert len(result) == 1
        assert result[0]["id"] == 1


# -------------------------------------------------------
# UNIT ТЕСТИ — Форматування дати відгуку
# -------------------------------------------------------

class TestReviewDateFormat:

    def test_current_year_no_year_shown(self):
        """Поточний рік — рік не відображається."""
        now = datetime.now()
        date_str = f"{now.year}-03-15T10:30:00"
        result = format_review_date(date_str)
        assert str(now.year) not in result
        assert "березня" in result

    def test_past_year_shown(self):
        """Минулий рік — рік відображається."""
        result = format_review_date("2023-05-20T12:00:00")
        assert "2023" in result
        assert "травня" in result

    def test_day_correct(self):
        result = format_review_date("2023-01-07T00:00:00")
        assert result.startswith("7")


# -------------------------------------------------------
# UNIT ТЕСТИ — Розрахунок суми контракту
# -------------------------------------------------------

class TestContractCalculation:

    def test_one_month(self):
        """30 днів = 1 місяць = ціна за місяць."""
        total = calculate_total_sum(
            price_per_month=6000.0,
            start_date=date(2026, 6, 1),
            end_date=date(2026, 7, 1)
        )
        assert total == 6000.0

    def test_two_weeks(self):
        """15 днів ≈ пів місяця."""
        total = calculate_total_sum(
            price_per_month=6000.0,
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 16)
        )
        assert total == 3000.0

    def test_zero_days(self):
        """Однакові дати — 0."""
        total = calculate_total_sum(
            price_per_month=5000.0,
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 1)
        )
        assert total == 0.0


# -------------------------------------------------------
# UNIT ТЕСТИ — Валідація схем Pydantic
# -------------------------------------------------------

class TestSchemaValidation:

    def test_apartment_create_requires_title(self):
        from pydantic import ValidationError
        from schemas import ApartmentCreate
        with pytest.raises(ValidationError):
            ApartmentCreate(
                description="Опис",
                city="Київ",
                type="Квартира",
                area=50,
                price=5000,
                room_count=2
                # title відсутній
            )

    def test_apartment_create_telegram_optional(self):
        from schemas import ApartmentCreate
        apt = ApartmentCreate(
            title="Тест",
            description="Опис",
            city="Київ",
            type="Квартира",
            area=50,
            price=5000,
            room_count=2
        )
        assert apt.telegram is None

    def test_person_create_requires_password(self):
        from pydantic import ValidationError
        from schemas import PersonCreate
        from models import UserRole
        with pytest.raises(ValidationError):
            PersonCreate(
                name="Тест",
                surname="Юзер",
                phone_number="0991234567",
                id_card_series="АА000001",
                role=UserRole.client
                # password відсутній
            )
