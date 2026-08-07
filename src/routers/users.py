# from fastapi import APIRouter, Depends, status,HTTPException
# from sqlalchemy.orm import Session
# from typing import List

# import crud, schemas
# from database import get_db

# router = APIRouter(
#     prefix="/api/users",
#     tags=["Users / Persons"]
# )

# @router.post("/", response_model=schemas.PersonResponse, status_code=status.HTTP_201_CREATED)
# def create_user(user: schemas.PersonCreate, db: Session = Depends(get_db)):
#     return crud.create_person(db=db, person=user)

# @router.get("/", response_model=List[schemas.PersonResponse])
# def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     return crud.get_persons(db, skip=skip, limit=limit)


# @router.get("/{user_id}", response_model=schemas.PersonResponse)
# def get_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = crud.get_person(db, person_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="Користувача не знайдено")
#     return db_user

# @router.patch("/{user_id}", response_model=schemas.PersonResponse)
# def update_user(user_id: int, user_data: schemas.PersonUpdate, db: Session = Depends(get_db)):
#     db_user = crud.update_person(db, person_id=user_id, person_data=user_data)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="Користувача не знайдено")
#     return db_user

# @router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = crud.get_person(db, person_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="Користувача не знайдено")
#     crud.delete_person(db, person_id=user_id)
#     return






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
