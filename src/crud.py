from sqlalchemy.orm import Session
from fastapi import HTTPException
import models, schemas,auth


# ==========================================
#                 ADDRESS
# ==========================================
def create_address(db: Session, address: schemas.AddressCreate):
    db_address = models.Address(**address.model_dump())
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address

# ==========================================
#             USERS / PERSONS
# ==========================================
def create_person(db: Session, person: schemas.PersonCreate):
    hashed_pwd = auth.get_password_hash(person.password)
    db_person = models.Person(
        name=person.name,
        surname=person.surname,
        email=person.email,
        hashed_password=hashed_pwd,
        phone_number=person.phone_number,
        date_of_birth=person.date_of_birth,
        role=person.role
    )
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    
    

    return db_person

def get_persons(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Person).offset(skip).limit(limit).all()

def get_person(db: Session, person_id: int):
    return db.query(models.Person).filter(models.Person.id == person_id).first()

def update_person(db: Session, person_id: int, person_data: schemas.PersonUpdate):
    db_person = get_person(db, person_id)
    if db_person:
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
    return db_person

def get_user_by_email(db: Session, email: str):
    return db.query(models.Person).filter(models.Person.email == email).first()

# ==========================================
#               APARTMENTS
# ==========================================
def create_apartment(db: Session, apartment: schemas.ApartmentCreate):
    db_apartment = models.Apartment(**apartment.model_dump())
    db.add(db_apartment)
    db.commit()
    db.refresh(db_apartment)
    return db_apartment

def get_apartments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Apartment).offset(skip).limit(limit).all()

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


