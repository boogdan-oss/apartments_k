from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import insert
import models, schemas, auth
from base_repository import BaseRepository
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



class OwnerRepository(PersonRepository):

    def __init__(self):
       
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
            telegram=schema.telegram,
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)
        return owner

    # ООП: Розширення — новий метод якого немає в батьківському класі
    def get_with_apartments(self, db: Session, owner_id: int) -> Optional[models.Owner]:
        return db.query(models.Owner).filter(models.Owner.id == owner_id).first()

    def promote_from_client(self, db: Session, person_id:int) -> None:
        """Змінює роль з client на owner при першому оголошенні."""


        person = db.query(models.Person).filter(models.Person.id == person_id).first()
        if not person:
             return # або викинути помилку
    
        person.role = models.UserRole.owner

    # 2. Вставляємо запис прямо в таблицю owner, минаючи ORM-мапер успадкування
        db.execute(
            insert(models.Owner).values(id=person_id)
         )
            
        db.commit()


    def demote_to_client(self, db: Session, person: models.Person) -> None:
        """Повертає роль client якщо не залишилось оголошень."""
        person.role = models.UserRole.client
        db.add(person)
        db.flush()



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




class ApartmentRepository(BaseRepository[models.Apartment, schemas.ApartmentCreate, schemas.ApartmentUpdate]):

    def __init__(self):
        super().__init__(models.Apartment)

    # ООП: Реалізація abstractmethod create()
    def create(self, db: Session, schema: schemas.ApartmentCreate,
            owner_id: int = None) -> models.Apartment:
        apartment = models.Apartment(
            title=schema.title,
            description=schema.description,
            city=schema.city,
            type=schema.type,
            img=schema.img,
            area=schema.area,
            price=schema.price,
            room_count=schema.room_count,
            address_id=schema.address_id,
            owner_id=owner_id,  # ✅ явно передаємо
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
