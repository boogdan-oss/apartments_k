from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

import models, schemas, auth
from base_repository import BaseRepository


# =======================================================
# ООП: ІЄРАРХІЯ РЕПОЗИТОРІЇВ ДЛЯ PERSON
#
#   BaseRepository (абстрактний, Generic)
#       └── PersonRepository      (базовий для людей)
#               ├── OwnerRepository   (власник)
#               └── ClientRepository  (орендар)
# =======================================================


# -------------------------------------------------------
# ООП: Конкретний клас — PersonRepository
# Принцип: Наслідування від BaseRepository.
# Принцип: Реалізує abstractmethod create().
# Принцип: Є батьківським для Owner і Client репозиторіїв.
# -------------------------------------------------------
class PersonRepository(BaseRepository[models.Person, schemas.PersonCreate, schemas.PersonUpdate]):

    def __init__(self):
        super().__init__(models.Person)

    # ООП: Реалізація abstractmethod — обов'язкова
    def create(self, db: Session, schema: schemas.PersonCreate) -> models.Person:
        person = models.Person(
            name           = schema.name,
            surname        = schema.surname,
            email          = schema.email,
            phone_number   = schema.phone_number,
            date_of_birth  = schema.date_of_birth,
            id_card_series = schema.id_card_series,
            hashed_password= auth.get_password_hash(schema.password),
            role           = schema.role,
        )
        db.add(person)
        db.commit()
        db.refresh(person)
        return person

    # Розширення — специфічний метод тільки для Person
    def get_by_email(self, db: Session, email: str) -> Optional[models.Person]:
        return db.query(self.model).filter(self.model.email == email).first()


# -------------------------------------------------------
# ООП: Дочірній клас — OwnerRepository
# Принцип: Наслідування від PersonRepository.
# Принцип: Override create() — створює Owner (підклас Person).
# Принцип: Розширення — додає get_with_apartments().
# -------------------------------------------------------
class OwnerRepository(PersonRepository):

    def __init__(self):
        # ООП: super().__init__() — виклик батьківського конструктора
        # але модель перевизначаємо на Owner
        BaseRepository.__init__(self, models.Owner)

    # ООП: Override — перевизначаємо create() для Owner
    def create(self, db: Session, schema: schemas.PersonCreate) -> models.Owner:
        owner = models.Owner(
            name           = schema.name,
            surname        = schema.surname,
            email          = schema.email,
            phone_number   = schema.phone_number,
            date_of_birth  = schema.date_of_birth,
            id_card_series = schema.id_card_series,
            hashed_password= auth.get_password_hash(schema.password),
            role           = models.UserRole.owner,  # роль фіксована
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)
        return owner

    # ООП: Розширення — новий метод якого немає в батьківському класі
    def get_with_apartments(self, db: Session, owner_id: int) -> Optional[models.Owner]:
        return db.query(models.Owner).filter(models.Owner.id == owner_id).first()

    def promote_from_client(self, db: Session, person: models.Person) -> None:
        """Змінює роль з client на owner при першому оголошенні."""
        person.role = models.UserRole.owner
        db.add(person)
        db.flush()

    def demote_to_client(self, db: Session, person: models.Person) -> None:
        """Повертає роль client якщо не залишилось оголошень."""
        person.role = models.UserRole.client
        db.add(person)
        db.flush()


# -------------------------------------------------------
# ООП: Дочірній клас — ClientRepository
# Принцип: Наслідування від PersonRepository.
# Принцип: Override create() — створює Client.
# Принцип: Розширення — get_contracts().
# -------------------------------------------------------
class ClientRepository(PersonRepository):

    def __init__(self):
        BaseRepository.__init__(self, models.Client)

    # ООП: Override — своя реалізація create() для Client
    def create(self, db: Session, schema: schemas.PersonCreate) -> models.Client:
        client = models.Client(
            name                 = schema.name,
            surname              = schema.surname,
            email                = schema.email,
            phone_number         = schema.phone_number,
            date_of_birth        = schema.date_of_birth,
            id_card_series       = schema.id_card_series,
            hashed_password      = auth.get_password_hash(schema.password),
            role                 = models.UserRole.client,  # роль фіксована
            id_card_series_extra = schema.id_card_series,
        )
        db.add(client)
        db.commit()
        db.refresh(client)
        return client

    # ООП: Розширення — метод специфічний тільки для клієнта
    def get_contracts(self, db: Session, client_id: int):
        return db.query(models.Contract).filter(
            models.Contract.client_id == client_id
        ).all()


# =======================================================
# ООП: ApartmentRepository — окрема гілка від BaseRepository
# (не пов'язана з PersonRepository)
# =======================================================

class ApartmentRepository(BaseRepository[models.Apartment, schemas.ApartmentCreate, schemas.ApartmentUpdate]):

    def __init__(self):
        super().__init__(models.Apartment)

    # ООП: Реалізація abstractmethod create()
    def create(self, db: Session, schema: schemas.ApartmentCreate,
               owner_id: int = None) -> models.Apartment:
        apartment = models.Apartment(
            **schema.model_dump(),
            owner_id=owner_id,
            status="pending",
        )
        db.add(apartment)
        db.commit()
        db.refresh(apartment)
        return apartment

    # ООП: Розширення — специфічні методи тільки для квартир
    def get_active(self, db: Session, skip: int = 0, limit: int = 100) -> list:
        return (
            db.query(self.model)
            .filter(self.model.status == "active")
            .offset(skip).limit(limit).all()
        )

    def get_by_owner(self, db: Session, owner_id: int) -> list:
        return db.query(self.model).filter(self.model.owner_id == owner_id).all()

    def delete_with_role_check(self, db: Session, apartment_id: int,
                               current_user: models.Person) -> models.Apartment:
        apartment = self.get(db, apartment_id)
        if not apartment:
            raise HTTPException(status_code=404, detail="Оголошення не знайдено")
        if apartment.owner_id != current_user.id and current_user.role != models.UserRole.admin:
            raise HTTPException(status_code=403, detail="Немає прав на видалення")

        db.delete(apartment)
        db.flush()

        remaining = db.query(self.model).filter(
            self.model.owner_id == current_user.id
        ).count()

        if remaining == 0 and current_user.role == models.UserRole.owner:
            current_user.role = models.UserRole.client
            db.add(current_user)

        db.commit()
        return apartment


# -------------------------------------------------------
# Singleton-like екземпляри — імпортуються в роутерах
# -------------------------------------------------------
person_repo   = PersonRepository()
owner_repo    = OwnerRepository()
client_repo   = ClientRepository()
apartment_repo= ApartmentRepository()
