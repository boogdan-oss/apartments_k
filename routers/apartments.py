from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models import Apartment
import crud, schemas, models
from database import get_db

router = APIRouter(
    prefix="/api/apartments",
    tags=["Apartments"]
)

@router.post("/", response_model=schemas.ApartmentResponse, status_code=status.HTTP_201_CREATED)
def create_apartment(apartment: schemas.ApartmentCreate, db: Session = Depends(get_db)):
    # Перевіряємо чи існує власник (Owner)
    if not db.query(models.Owner).filter(models.Owner.id == apartment.owner_id).first():
        raise HTTPException(status_code=404, detail="Власник не знайдений")
        
   
    # if not db.query(models.Address).filter(models.Address.id == apartment.address_id).first():
    #     raise HTTPException(status_code=404, detail="Адреса не знайдена")

    return crud.create_apartment(db=db, apartment=apartment)

@router.get("/", response_model=List[schemas.ApartmentResponse])
def read_apartments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_apartments(db, skip=skip, limit=limit)

@router.get("/{apartment_id}", response_model=schemas.ApartmentResponse)
def get_apartment(apartment_id: int, db: Session = Depends(get_db)):
    db_apartment = crud.get_apartment(db, apartment_id=apartment_id)
    if db_apartment is None:
        raise HTTPException(status_code=404, detail="Квартиру не знайдено")
    return db_apartment

@router.get("/listing/{listing_id}")
def get_listing_details(listing_id: int, db: Session = Depends(get_db)):
    # Шукаємо квартиру
    listing = db.query(Apartment).filter(Apartment.id == listing_id).first()
    
    if not listing:
        raise HTTPException(status_code=404, detail="Квартиру не знайдено")
        
    
    return {
        "id": listing.id,
        "title": listing.title,
        "price": listing.price,
        "description": listing.description,
        "img": listing.img,
        # Дані власника беремо зі зв'язаної таблиці!
        "owner": {
            "name": listing.owner.person.name,
            "surname": listing.owner.person.surname,
            "email": listing.owner.person.email
        }
    }

@router.patch("/{apartment_id}", response_model=schemas.ApartmentResponse)
def update_apartment(apartment_id: int, apartment_data: schemas.ApartmentUpdate, db: Session = Depends(get_db)):
    db_apartment = crud.update_apartment(db, apartment_id=apartment_id, apartment_data=apartment_data)
    if db_apartment is None:
        raise HTTPException(status_code=404, detail="Квартиру не знайдено")
    return db_apartment

@router.delete("/{apartment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_apartment(apartment_id: int, db: Session = Depends(get_db)):
    db_apartment = crud.get_apartment(db, apartment_id=apartment_id)
    if db_apartment is None:
        raise HTTPException(status_code=404, detail="Квартиру не знайдено")
    crud.delete_apartment(db, apartment_id=apartment_id)
    return