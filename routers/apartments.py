# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from typing import List
# from models import Apartment
# import crud, schemas, models
# from database import get_db
# from routers.auth import get_current_user

# router = APIRouter(
#     prefix="/api/apartments",
#     tags=["Apartments"]
# )



# @router.post("/",response_model=schemas.ApartmentResponse)
# def create_apartmet_new(
#     apartment: schemas.ApartmentCreate,
#     db:Session=Depends(get_db),
#     current_user:models.Person=Depends(get_current_user)
#     ):
#     if current_user.role == models.UserRole.client:
#         current_user.role = models.UserRole.owner  # або "owner" якщо не enum
#         db.add(current_user)
    
#     new_apartment=models.Apartment(
#         title=apartment.title,
#         description=apartment.description,
#         city=apartment.city,
#         type=apartment.type,
#         img=apartment.img,
#         area=apartment.area,
#         price=apartment.price,
#         room_count=apartment.room_count,
#         owner_id=current_user.id,
#         address_id=apartment.address_id,
#        status=models.ApartmentStatus.pending

#     )
#     db.add(new_apartment)
    
#     db.commit()

#     db.refresh(new_apartment)
#     return new_apartment



# @router.put("/{apartment_id}", response_model=schemas.ApartmentResponse)
# def update_apartment(
#     apartment_id: int, 
#     apartment_data: schemas.ApartmentUpdate, 
#     db: Session = Depends(get_db)
#     # current_user: models.Person = Depends(get_current_user) # Можна додати перевірку, що це адмін
# ):
#     # 1. Шукаємо квартиру в базі
#     db_apartment = db.query(models.Apartment).filter(models.Apartment.id == apartment_id).first()
    
#     if not db_apartment:
#         raise HTTPException(status_code=404, detail="Оголошення не знайдено")

#     # 2. Оновлюємо тільки ті поля, які прислав фронтенд
#     update_data = apartment_data.dict(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(db_apartment, key, value)

#     # 3. Зберігаємо зміни
#     db.commit()
#     db.refresh(db_apartment)
    
#     return db_apartment

# @router.get("/my-listings", response_model=List[schemas.ApartmentResponse])
# def get_my_listings(db: Session = Depends(get_db), current_user: models.Person = Depends(get_current_user)):
   
   
#     return db.query(models.Apartment).filter(models.Apartment.owner_id == current_user.id).all()



# @router.get("/favorites", response_model=List[schemas.ApartmentResponse])
# def get_my_favorites(db: Session = Depends(get_db), current_user: models.Person = Depends(get_current_user)):
#     # Знаходимо всі записи в таблиці favorites для цього юзера
#     favorites = db.query(models.Favorite).filter(models.Favorite.user_id == current_user.id).all()
    
   
#     return [fav.apartment for fav in favorites]


# @router.get("/", response_model=List[schemas.ApartmentResponse])
# def read_apartments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     # return crud.get_apartments(db, skip=skip, limit=limit)
#          apartments=db.query(models.Apartment).filter(models.Apartment.status=="active").all()
#          return apartments

# @router.get("/{apartment_id}", response_model=schemas.ApartmentResponse)
# def get_apartment(apartment_id: int, db: Session = Depends(get_db)):
#     db_apartment = crud.get_apartment(db, apartment_id=apartment_id)
#     if db_apartment is None:
#         raise HTTPException(status_code=404, detail="Квартиру не знайдено")
#     return db_apartment

# @router.get("/listing/{listing_id}")
# def get_listing_details(listing_id: int, db: Session = Depends(get_db)):
#     listing = db.query(Apartment).filter(Apartment.id == listing_id).first()
    
#     if not listing:
#         raise HTTPException(status_code=404, detail="Квартиру не знайдено")
        
    
#     return {
#         "id": listing.id,
#         "title": listing.title,
#         "price": listing.price,
#         "description": listing.description,
#         "img": listing.img,
#         "city":listing.city,
#         "type":listing.type,
#         # Дані власника беремо зі зв'язаної таблиці!
#         "owner": {
#             "name": listing.owner.name,
#             "surname": listing.owner.surname,
#             "email": listing.owner.email
#         }
#     }

# @router.patch("/{apartment_id}", response_model=schemas.ApartmentResponse)
# def update_apartment(apartment_id: int, apartment_data: schemas.ApartmentUpdate, db: Session = Depends(get_db)):
#     db_apartment = crud.update_apartment(db, apartment_id=apartment_id, apartment_data=apartment_data)
#     if db_apartment is None:
#         raise HTTPException(status_code=404, detail="Квартиру не знайдено")
#     return db_apartment

# @router.delete("/{apartment_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_apartment(apartment_id: int, db: Session = Depends(get_db)):
#     db_apartment = crud.get_apartment(db, apartment_id=apartment_id)
#     if db_apartment is None:
#         raise HTTPException(status_code=404, detail="Квартиру не знайдено")
#     crud.delete_apartment(db, apartment_id=apartment_id)
#     return

# from fastapi import HTTPException, status

# @router.delete("/listing/{apartment_id}")
# def delete_apartment(
#     apartment_id: int, 
#     db: Session = Depends(get_db), 
#     current_user: models.Person = Depends(get_current_user)
# ):
#     # 1. Шукаємо квартиру в базі
#     apartment = db.query(models.Apartment).filter(models.Apartment.id == apartment_id).first()
    
#     # 2. Якщо такої квартири немає
#     if not apartment:
#         raise HTTPException(status_code=404, detail="Оголошення не знайдено")
        
   
#     if apartment.owner_id != current_user.id and current_user.role != "admin":
#         raise HTTPException(status_code=403, detail="Ви не можете видалити чуже оголошення!")

#     # 4. Видаляємо з бази
#     db.delete(apartment)
#     db.commit()
    
#     return {"message": "Оголошення успішно видалено"}

# #---------------------------------------------------------------------------------------



# @router.post("/favorites/{apartment_id}")
# def add_to_favorites(apartment_id: int, db: Session = Depends(get_db), current_user: models.Person = Depends(get_current_user)):
#     # Перевіряємо, чи вже є в улюблених
#     existing = db.query(models.Favorite).filter(
#         models.Favorite.user_id == current_user.id, 
#         models.Favorite.apartment_id == apartment_id
#     ).first()
    
#     if existing:
#         return {"message": "Вже в улюблених"}

#     new_favorite = models.Favorite(user_id=current_user.id, apartment_id=apartment_id)
#     db.add(new_favorite)
#     db.commit()
#     return {"message": "Додано в улюблені"}
# # 4. ВИДАЛИТИ З УЛЮБЛЕНИХ
# @router.delete("/favorites/{apartment_id}")
# def remove_from_favorites(apartment_id: int, db: Session = Depends(get_db), current_user: models.Person = Depends(get_current_user)):
#     fav = db.query(models.Favorite).filter(
#         models.Favorite.user_id == current_user.id, 
#         models.Favorite.apartment_id == apartment_id
#     ).first()
    
#     if not fav:
#         raise HTTPException(status_code=404, detail="Не знайдено в улюблених")
        
#     db.delete(fav)
#     db.commit()
#     return {"message": "Видалено"}









from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import schemas, models
from database import get_db
from routers.auth import get_current_user
from repositories import apartment_repo, owner_repo

router = APIRouter(prefix="/api/apartments", tags=["Apartments"])

# ВАЖЛИВО: статичні маршрути ВИЩЕ динамічних /{id}

@router.get("/my-listings", response_model=List[schemas.ApartmentResponse])
def get_my_listings(db: Session = Depends(get_db),
                    current_user: models.Person = Depends(get_current_user)):
    return apartment_repo.get_by_owner(db, owner_id=current_user.id)


@router.get("/favorites", response_model=List[schemas.ApartmentResponse])
def get_favorites(db: Session = Depends(get_db),
                  current_user: models.Person = Depends(get_current_user)):
    favs = db.query(models.Favorite).filter(
        models.Favorite.user_id == current_user.id).all()
    return [f.apartment for f in favs]


@router.post("/favorites/{apartment_id}")
def add_favorite(apartment_id: int, db: Session = Depends(get_db),
                 current_user: models.Person = Depends(get_current_user)):
    exists = db.query(models.Favorite).filter(
        models.Favorite.user_id == current_user.id,
        models.Favorite.apartment_id == apartment_id).first()
    if exists:
        return {"message": "Вже в улюблених"}
    db.add(models.Favorite(user_id=current_user.id, apartment_id=apartment_id))
    db.commit()
    return {"message": "Додано"}


@router.delete("/favorites/{apartment_id}")
def remove_favorite(apartment_id: int, db: Session = Depends(get_db),
                    current_user: models.Person = Depends(get_current_user)):
    fav = db.query(models.Favorite).filter(
        models.Favorite.user_id == current_user.id,
        models.Favorite.apartment_id == apartment_id).first()
    if not fav:
        raise HTTPException(status_code=404, detail="Не знайдено")
    db.delete(fav)
    db.commit()
    return {"message": "Видалено"}


@router.get("/", response_model=List[schemas.ApartmentResponse])
def read_apartments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return apartment_repo.get_active(db, skip=skip, limit=limit)


@router.post("/", response_model=schemas.ApartmentResponse, status_code=status.HTTP_201_CREATED)
def create_apartment(schema: schemas.ApartmentCreate, db: Session = Depends(get_db),
                     current_user: models.Person = Depends(get_current_user)):
    # ООП: OwnerRepository підвищує роль при першому оголошенні
    if current_user.role == models.UserRole.client:
        owner_repo.promote_from_client(db, current_user)
    return apartment_repo.create(db, schema, owner_id=current_user.id)


@router.get("/{apartment_id}", response_model=schemas.ApartmentResponse)
def get_apartment(apartment_id: int, db: Session = Depends(get_db)):
    apt = apartment_repo.get(db, apartment_id)
    if not apt:
        raise HTTPException(status_code=404, detail="Не знайдено")
    return apt


@router.patch("/{apartment_id}", response_model=schemas.ApartmentResponse)
def update_apartment(apartment_id: int, schema: schemas.ApartmentUpdate,
                     db: Session = Depends(get_db),
                     current_user: models.Person = Depends(get_current_user)):
    apt = apartment_repo.get(db, apartment_id)
    if not apt:
        raise HTTPException(status_code=404, detail="Не знайдено")
    if apt.owner_id != current_user.id and current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Немає прав")
    return apartment_repo.update(db, apt, schema)


@router.delete("/{apartment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_apartment(apartment_id: int, db: Session = Depends(get_db),
                     current_user: models.Person = Depends(get_current_user)):
    apartment_repo.delete_with_role_check(db, apartment_id, current_user)
