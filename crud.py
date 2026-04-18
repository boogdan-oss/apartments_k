from sqlalchemy.orm import Session
from typing import Optional
import models, schemas
# --- USERS ---
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    # Увага: Для реального проєкту тут має бути хешування пароля (наприклад, bcrypt)
    # Поки що для MVP залишаємо як є, щоб швидко протестувати
    fake_hashed_password = user.password 
    
    db_user = models.User(
        email=user.email,
        hashed_password=fake_hashed_password,
        name=user.name,
        phone=user.phone,
        telegram_link=user.telegram_link
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_data: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if db_user:
        # Оновлюємо лише ті поля, які були передані
        update_data = user_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user
# --- PROPERTIES ---
def get_properties(
    db: Session, 
    city: Optional[str] = None, 
    min_price: Optional[float] = None, 
    max_price: Optional[float] = None,
    only_active: bool = True
):
    # Починаємо формувати запит
    query = db.query(models.Property)

    # Показувати тільки активні (для стрічки орендаря)
    if only_active:
        query = query.filter(models.Property.is_active == True)

    # Фільтр по місту (якщо передано)
    if city:
        query = query.filter(models.Property.city.ilike(f"%{city}%"))

    # Фільтр по мінімальній ціні
    if min_price is not None:
        query = query.filter(models.Property.price >= min_price)

    # Фільтр по максимальній ціні
    if max_price is not None:
        query = query.filter(models.Property.price <= max_price)

    return query.all()

def create_property(db: Session, property: schemas.PropertyCreate, owner_id: int):
    db_property = models.Property(**property.model_dump(), owner_id=owner_id)
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property

def update_property_status(db: Session, property_id: int, is_active: bool):
    db_property = db.query(models.Property).filter(models.Property.id == property_id).first()
    if db_property:
        db_property.is_active = is_active
        db.commit()
        db.refresh(db_property)
    return db_property