from pydantic import BaseModel, EmailStr
from typing import Optional, List
from decimal import Decimal

# --- PHOTOS ---
class PhotoBase(BaseModel):
    url: str

class PhotoResponse(PhotoBase):
    id: int
    class Config:
        from_attributes = True

# --- USERS ---
class UserBase(BaseModel):
    email: EmailStr
    name: str
    phone: str
    telegram_link: Optional[str] = None

class UserCreate(UserBase):
    password: str # Приймаємо пароль, але в БД піде хеш

    # --- USERS ---
class UserBase(BaseModel):
    email: str # Використовуємо str, оскільки виникали проблеми з email-validator
    name: str
    phone: str
    telegram_link: Optional[str] = None

class UserCreate(UserBase):
    password: str 

# Нова схема для оновлення (всі поля необов'язкові)
class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    telegram_link: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_admin: bool
    class Config:
        from_attributes = True

class UserResponse(UserBase):
    id: int
    is_admin: bool
    class Config:
        from_attributes = True

# --- PROPERTIES ---
class PropertyBase(BaseModel):
    title: str
    description: str
    price: Decimal
    city: str
    address: str
    is_active: bool = True

class PropertyCreate(PropertyBase):
    pass # Власник буде братися з токена авторизації (поки що можна передавати owner_id)

class PropertyUpdateStatus(BaseModel):
    is_active: bool

class PropertyResponse(PropertyBase):
    id: int
    owner_id: int
    owner: UserResponse  # Щоб в картці об'єкта одразу був телефон/телеграм власника
    photos: List[PhotoResponse] = []

    class Config:
        from_attributes = True