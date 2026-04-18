from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

import crud, schemas, models
from database import get_db

router = APIRouter(
    prefix="/api/properties",
    tags=["Properties"]
)

@router.get("/", response_model=List[schemas.PropertyResponse])
def read_properties(
    city: Optional[str] = Query(None, description="Фільтр за містом"),
    min_price: Optional[float] = Query(None, description="Мінімальна ціна"),
    max_price: Optional[float] = Query(None, description="Максимальна ціна"),
    db: Session = Depends(get_db)
):
    return crud.get_properties(db, city=city, min_price=min_price, max_price=max_price)

@router.post("/", response_model=schemas.PropertyResponse)
def create_property(property: schemas.PropertyCreate, owner_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == owner_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    return crud.create_property(db, property, owner_id)

@router.patch("/{property_id}/status", response_model=schemas.PropertyResponse)
def change_status(property_id: int, status_update: schemas.PropertyUpdateStatus, db: Session = Depends(get_db)):
    updated_property = crud.update_property_status(db, property_id, status_update.is_active)
    if not updated_property:
        raise HTTPException(status_code=404, detail="Оголошення не знайдено")
    return updated_property

@router.delete("/{property_id}")
def delete_property(property_id: int, db: Session = Depends(get_db)):
    db_property = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not db_property:
        raise HTTPException(status_code=404, detail="Оголошення не знайдено")
    db.delete(db_property)
    db.commit()
    return {"detail": "Оголошення успішно видалено"}