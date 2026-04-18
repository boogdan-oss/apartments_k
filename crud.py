from sqlalchemy.orm import Session
import models, schemas

# ==========================================
# ADDRESS (Адреси)
# ==========================================
def create_address(db: Session, address: schemas.AddressCreate):
    db_address = models.Address(**address.model_dump())
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address

def get_address(db: Session, address_id: int):
    return db.query(models.Address).filter(models.Address.id == address_id).first()


# ==========================================
# PERSON / ROLES (Користувачі та їх ролі)
# ==========================================
def create_owner(db: Session, person: schemas.PersonCreate):
    # 1. Спочатку створюємо базовий запис у таблиці Person
    db_person = models.Person(**person.model_dump())
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    
    # 2. Потім створюємо запис у таблиці Owner, прив'язаний по ID
    db_owner = models.Owner(id=db_person.id)
    db.add(db_owner)
    db.commit()
    db.refresh(db_owner)
    
    return db_person # Повертаємо дані Person, оскільки ID співпадають

def get_person(db: Session, person_id: int):
    return db.query(models.Person).filter(models.Person.id == person_id).first()


# ==========================================
# APARTMENT (Об'єкти нерухомості - Повний CRUD)
# ==========================================
def create_apartment(db: Session, apartment: schemas.ApartmentCreate):
    db_apartment = models.Apartment(**apartment.model_dump())
    db.add(db_apartment)
    db.commit()
    db.refresh(db_apartment)
    return db_apartment

def get_apartment(db: Session, apartment_id: int):
    return db.query(models.Apartment).filter(models.Apartment.id == apartment_id).first()

def get_apartments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Apartment).offset(skip).limit(limit).all()

def update_apartment(db: Session, apartment_id: int, apartment_data: schemas.ApartmentCreate):
    db_apartment = get_apartment(db, apartment_id)
    if db_apartment:
        # Оновлюємо поля динамічно
        for key, value in apartment_data.model_dump().items():
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


# ==========================================
# CONTRACT (Договори)
# ==========================================
def create_contract(db: Session, contract: schemas.ContractCreate):
    db_contract = models.Contract(**contract.model_dump())
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract

def get_contracts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Contract).offset(skip).limit(limit).all()