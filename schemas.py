from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal
from models import UserRole

# --- PERSON ---
class PersonBase(BaseModel):
    name: str
    surname: str
    middle_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: str
    date_of_birth: Optional[date] = None
    role: UserRole # Додали роль

class PersonCreate(PersonBase):
   
    id_card_series: Optional[str] = None 
    password: str
    

class PersonUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None    

class PersonResponse(PersonBase):
    id: int
    class Config:
        from_attributes = True

# --- ADDRESS ---
class AddressBase(BaseModel):
    street: str
    building: str
    apartment_number: str

class AddressCreate(AddressBase):
    pass

class AddressResponse(AddressBase):
    id: int
    class Config:
        from_attributes = True

# --- APARTMENT ---
class ApartmentBase(BaseModel):
    title: str               # ДОДАНО: Заголовок
    description: str         # ДОДАНО: Опис
    city: str                # ДОДАНО: Місто
    type: str                # ДОДАНО: Тип житла (квартира/будинок)
    img: Optional[str] = None # ДОДАНО: Посилання на фото
    area: Decimal
    price: Decimal
    room_count: int
    street:Optional[str]=None
    address_id: Optional[int] = None # Зробили необов'язковим для спрощення
    owner_id: int

class ApartmentCreate(ApartmentBase):
    pass

class ApartmentUpdate(BaseModel):
    area: Optional[Decimal] = None
    price: Optional[Decimal] = None
    room_count: Optional[int] = None

class ApartmentResponse(ApartmentBase):
    id: int
    class Config:
        from_attributes = True

# --- CONTRACT ---
class ContractBase(BaseModel):
    apartment_id: int
    client_id: int
    contract_date: date
    total_sum: Decimal

class ContractCreate(BaseModel):
    apartment_id: int
    total_sum: Decimal
   

class ContractStatusUpdate(BaseModel):
    status: str # Сюди будемо передавати "approved" або "rejected"

class ContractResponse(ContractBase):
    id: int
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
        