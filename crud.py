from sqlalchemy.orm import Session
from fastapi import HTTPException
import models, schemas

# --- USERS / PERSONS ---
def get_person(db: Session, person_id: int):
    return db.query(models.Person).filter(models.Person.id == person_id).first()

def update_person(db: Session, person_id: int, person_data: schemas.PersonUpdate):
    db_person = get_person(db, person_id)
    if db_person:
        # exclude_unset=True означає, що ми беремо лише ті поля, які користувач реально передав
        update_data = person_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_person, key, value)
        db.commit()
        db.refresh(db_person)
    return db_person

def delete_person(db: Session, person_id: int):
    db_person = get_person(db, person_id)
    if db_person:
        db.delete(db_person)
        db.commit()
        # Завдяки ondelete='CASCADE' у моделях, записи з owner/client видаляться автоматично!
    return db_person

def create_person(db: Session, person: schemas.PersonCreate):
    # 1. Створюємо базовий запис у таблиці Person
    db_person = models.Person(
        name=person.name,
        surname=person.surname,
        middle_name=person.middle_name,
        email=person.email,
        phone_number=person.phone_number,
        date_of_birth=person.date_of_birth,
        role=person.role
    )
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    
    # 2. Розподіляємо по таблицях залежно від ролі
    if person.role == models.UserRole.landlord:
        # Якщо орендодавець - створюємо Owner
        db_owner = models.Owner(id=db_person.id)
        db.add(db_owner)
        db.commit()
        
    elif person.role == models.UserRole.tenant:
        # Якщо орендар - створюємо Client (вимагає id_card_series)
        if not person.id_card_series:
            # Видаляємо щойно створену персону, бо сталася помилка
            db.delete(db_person) 
            db.commit()
            raise HTTPException(status_code=400, detail="Для орендаря обов'язково потрібна серія паспорта (id_card_series)")
            
        db_client = models.Client(id=db_person.id, id_card_series=person.id_card_series)
        db.add(db_client)
        db.commit()

    # Якщо admin - він залишається просто в таблиці Person (до нього немає додаткових полів)

    return db_person

def get_persons(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Person).offset(skip).limit(limit).all()

def get_apartment(db: Session, apartment_id: int):
    return db.query(models.Apartment).filter(models.Apartment.id == apartment_id).first()

def update_apartment(db: Session, apartment_id: int, apartment_data: schemas.ApartmentUpdate):
    db_apartment = get_apartment(db, apartment_id)
    if db_apartment:
        update_data = apartment_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_apartment, key, value)
        db.commit()
        db.refresh(db_apartment)
    return db_apartment

def delete_apartment(db: Session, apartment_id: int):
    db_apartment = get_apartment(db, apartment_id)
    if db_apartment:
        db.delete(db_apartment)
        db.commit()
    return db_apartment