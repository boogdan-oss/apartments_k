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
    # Поле потрібне тільки якщо role == tenant (орендар), бо воно йде в таблицю Client
    id_card_series: Optional[str] = None 

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
    area: Decimal
    price: Decimal
    room_count: int
    address_id: int
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
    realtor_id: int
    contract_date: date
    total_sum: Decimal

class ContractCreate(ContractBase):
    pass

class ContractResponse(ContractBase):
    id: int
    class Config:
        from_attributes = True