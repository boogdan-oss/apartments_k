from sqlalchemy.orm import Session
import models, schemas

def get_apartments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Apartment).offset(skip).limit(limit).all()

def create_apartment(db: Session, apartment: schemas.ApartmentCreate):
    db_apartment = models.Apartment(**apartment.model_dump())
    db.add(db_apartment)
    db.commit()
    db.refresh(db_apartment)
    return db_apartment