from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from database import get_db
from routers.auth import get_current_user

router = APIRouter(prefix="/api/addresses", tags=["Addresses"])


@router.get("/", response_model=List[schemas.AddressResponse])
def get_addresses(db: Session = Depends(get_db)):
    """Отримати всі адреси для випадаючого списку."""
    return db.query(models.Address).all()


@router.post("/", response_model=schemas.AddressResponse)
def create_address(
    address: schemas.AddressCreate,
    db: Session = Depends(get_db),
    current_user: models.Person = Depends(get_current_user),
):
    """Додати нову адресу."""
    db_address = models.Address(**address.model_dump())
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address