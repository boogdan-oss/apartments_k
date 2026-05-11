


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import schemas, models
from database import get_db
from routers.auth import get_current_user
from repositories import person_repo, owner_repo, client_repo

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post("/", response_model=schemas.PersonResponse, status_code=status.HTTP_201_CREATED)
def register(schema: schemas.PersonCreate, db: Session = Depends(get_db)):
    # ООП: Поліморфізм — вибираємо репозиторій залежно від ролі
    if db.query(models.Person).filter(models.Person.email == schema.email).first():
        raise HTTPException(status_code=400, detail="Email вже зайнятий")

    if schema.role == models.UserRole.owner:
        return owner_repo.create(db, schema)   # OwnerRepository.create()
    elif schema.role == models.UserRole.client:
        return client_repo.create(db, schema)  # ClientRepository.create()
    else:
        return person_repo.create(db, schema)  # PersonRepository.create() (admin)


@router.get("/", response_model=List[schemas.PersonResponse])
def get_all_users(db: Session = Depends(get_db),
                  current_user: models.Person = Depends(get_current_user)):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Тільки для адміна")
    return person_repo.get_all(db)  # успадкований метод з BaseRepository


@router.get("/me", response_model=schemas.PersonResponse)
def get_me(current_user: models.Person = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=schemas.PersonResponse)
def update_me(schema: schemas.PersonUpdate, db: Session = Depends(get_db),
              current_user: models.Person = Depends(get_current_user)):
    return person_repo.update(db, current_user, schema)  # успадкований update()


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db),
                current_user: models.Person = Depends(get_current_user)):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Тільки для адміна")
    person_repo.delete(db, user_id)  # успадкований delete()
