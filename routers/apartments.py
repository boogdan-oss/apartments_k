from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import crud, schemas, models
from database import get_db

router = APIRouter(
    prefix="/apartments",
    tags=["Apartments"]
)

@router.post("/", response_model=schemas.ApartmentResponse)
def create_apartment(apartment: schemas.ApartmentCreate, db: Session = Depends(get_db)):
    # Перевірки зовнішніх ключів перед створенням
    owner = db.query(models.Owner).filter(models.Owner.id == apartment.owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Власник не знайдений")
        
    address = db.query(models.Address).filter(models.Address.id == apartment.address_id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Адреса не знайдена")

    return crud.create_apartment(db=db, apartment=apartment)

@router.get("/", response_model=List[schemas.ApartmentResponse])
def read_apartments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    apartments = crud.get_apartments(db, skip=skip, limit=limit)
    return apartments