from fastapi import APIRouter, Depends, status,HTTPException
from sqlalchemy.orm import Session
from typing import List

import crud, schemas
from database import get_db

router = APIRouter(
    prefix="/api/users",
    tags=["Users / Persons"]
)

@router.post("/", response_model=schemas.PersonResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.PersonCreate, db: Session = Depends(get_db)):
    return crud.create_person(db=db, person=user)

@router.get("/", response_model=List[schemas.PersonResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_persons(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=schemas.PersonResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_person(db, person_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    return db_user

@router.patch("/{user_id}", response_model=schemas.PersonResponse)
def update_user(user_id: int, user_data: schemas.PersonUpdate, db: Session = Depends(get_db)):
    db_user = crud.update_person(db, person_id=user_id, person_data=user_data)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_person(db, person_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    crud.delete_person(db, person_id=user_id)
    return