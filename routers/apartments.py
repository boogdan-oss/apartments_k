
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import schemas, models
from models import Apartment
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



@router.get("/listing/{listing_id}")
def get_listing_details(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(Apartment).filter(Apartment.id == listing_id).first()
    
    if not listing:
        raise HTTPException(status_code=404, detail="Квартиру не знайдено")
        
    
    return {
        "id":          listing.id,
        "title":       listing.title,
        "price":       listing.price,
        "description": listing.description,
        "img":         listing.img,
        "city":        listing.city,
        "type":        listing.type,
        "area":        listing.area,
        "room_count":  listing.room_count,
        "status":      listing.status,
        "owner_id":    listing.owner_id,
        "address_id":  listing.address_id,
        "telegram":    listing.telegram,  
 
       
        "images": [
            {"id": img.id, "url": img.url, "is_main": img.is_main}
            for img in listing.images
        ],
 
        "owner": {
            "name":         listing.owner.name,
            "surname":      listing.owner.surname,
            "email":        listing.owner.email,
            "phone_number": listing.owner.phone_number,  
        }
    }


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
   

    
    # 1. Додаємо print, щоб побачити в консолі, чи заходить код в if
    existing_owner = db.query(models.Owner).filter(models.Owner.id == current_user.id).first()
    
    # 2. Якщо запису немає — створюємо його (навіть якщо роль чомусь вже "owner")
    if not existing_owner:
        owner_repo.promote_from_client(db, current_user.id)
        db.refresh(current_user) # Оновлюємо стан юзера

    # 3. Створюємо квартиру
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



       



