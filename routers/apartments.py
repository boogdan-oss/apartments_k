from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models import Apartment
import crud, schemas, models
from database import get_db
from routers.auth import get_current_user

router = APIRouter(
    prefix="/api/apartments",
    tags=["Apartments"]
)



@router.post("/",response_model=schemas.ApartmentResponse)
def create_apartmet_new(
    apartment: schemas.ApartmentCreate,
    db:Session=Depends(get_db),
    current_user:models.Person=Depends(get_current_user)
    ):
    new_apartment=models.Apartment(
        title=apartment.title,
        description=apartment.description,
        city=apartment.city,
        type=apartment.type,
        img=apartment.img,
        area=apartment.area,
        price=apartment.price,
        room_count=apartment.room_count,
        owner_id=current_user.id,
        address_id=apartment.address_id,
       status=models.ApartmentStatus.pending

    )
    db.add(new_apartment)
    if current_user.role=="tenant":
        current_user.role="owner" 
        db.add(current_user)
    db.commit()

    db.refresh(new_apartment)
    return new_apartment



@router.put("/{apartment_id}", response_model=schemas.ApartmentResponse)
def update_apartment(
    apartment_id: int, 
    apartment_data: schemas.ApartmentUpdate, 
    db: Session = Depends(get_db)
    # current_user: models.Person = Depends(get_current_user) # Можна додати перевірку, що це адмін
):
    # 1. Шукаємо квартиру в базі
    db_apartment = db.query(models.Apartment).filter(models.Apartment.id == apartment_id).first()
    
    if not db_apartment:
        raise HTTPException(status_code=404, detail="Оголошення не знайдено")

    # 2. Оновлюємо тільки ті поля, які прислав фронтенд
    update_data = apartment_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_apartment, key, value)

    # 3. Зберігаємо зміни
    db.commit()
    db.refresh(db_apartment)
    
    return db_apartment

@router.get("/my-listings", response_model=List[schemas.ApartmentResponse])
def get_my_listings(db: Session = Depends(get_db), current_user: models.Person = Depends(get_current_user)):
    owner_record = db.query(models.Owner).filter(models.Owner.id == current_user.id).first()
    
    if not owner_record:
        return [] # Якщо він ще нічого не виставив
   
    return db.query(models.Apartment).filter(models.Apartment.owner_id == owner_record.id).all()



@router.get("/favorites", response_model=List[schemas.ApartmentResponse])
def get_my_favorites(db: Session = Depends(get_db), current_user: models.Person = Depends(get_current_user)):
    # Знаходимо всі записи в таблиці favorites для цього юзера
    favorites = db.query(models.Favorite).filter(models.Favorite.user_id == current_user.id).all()
    
   
    return [fav.apartment for fav in favorites]


@router.get("/", response_model=List[schemas.ApartmentResponse])
def read_apartments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # return crud.get_apartments(db, skip=skip, limit=limit)
         apartments=db.query(models.Apartment).filter(models.Apartment.status=="active").all()
         return apartments

@router.get("/{apartment_id}", response_model=schemas.ApartmentResponse)
def get_apartment(apartment_id: int, db: Session = Depends(get_db)):
    db_apartment = crud.get_apartment(db, apartment_id=apartment_id)
    if db_apartment is None:
        raise HTTPException(status_code=404, detail="Квартиру не знайдено")
    return db_apartment

@router.get("/listing/{listing_id}")
def get_listing_details(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(Apartment).filter(Apartment.id == listing_id).first()
    
    if not listing:
        raise HTTPException(status_code=404, detail="Квартиру не знайдено")
        
    
    return {
        "id": listing.id,
        "title": listing.title,
        "price": listing.price,
        "description": listing.description,
        "img": listing.img,
        "city":listing.city,
        "type":listing.type,
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

from fastapi import HTTPException, status

@router.delete("/listing/{apartment_id}")
def delete_apartment(
    apartment_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.Person = Depends(get_current_user)
):
    # 1. Шукаємо квартиру в базі
    apartment = db.query(models.Apartment).filter(models.Apartment.id == apartment_id).first()
    
    # 2. Якщо такої квартири немає
    if not apartment:
        raise HTTPException(status_code=404, detail="Оголошення не знайдено")
        
   
    if apartment.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Ви не можете видалити чуже оголошення!")

    # 4. Видаляємо з бази
    db.delete(apartment)
    db.commit()
    
    return {"message": "Оголошення успішно видалено"}

#---------------------------------------------------------------------------------------



@router.post("/favorites/{apartment_id}")
def add_to_favorites(apartment_id: int, db: Session = Depends(get_db), current_user: models.Person = Depends(get_current_user)):
    # Перевіряємо, чи вже є в улюблених
    existing = db.query(models.Favorite).filter(
        models.Favorite.user_id == current_user.id, 
        models.Favorite.apartment_id == apartment_id
    ).first()
    
    if existing:
        return {"message": "Вже в улюблених"}

    new_favorite = models.Favorite(user_id=current_user.id, apartment_id=apartment_id)
    db.add(new_favorite)
    db.commit()
    return {"message": "Додано в улюблені"}
# 4. ВИДАЛИТИ З УЛЮБЛЕНИХ
@router.delete("/favorites/{apartment_id}")
def remove_from_favorites(apartment_id: int, db: Session = Depends(get_db), current_user: models.Person = Depends(get_current_user)):
    fav = db.query(models.Favorite).filter(
        models.Favorite.user_id == current_user.id, 
        models.Favorite.apartment_id == apartment_id
    ).first()
    
    if not fav:
        raise HTTPException(status_code=404, detail="Не знайдено в улюблених")
        
    db.delete(fav)
    db.commit()
    return {"message": "Видалено"}