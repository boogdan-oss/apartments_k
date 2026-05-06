from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal
from models import UserRole
#валідація.структура,репка і модулі

class PersonBase(BaseModel):
    name: str
    surname: str
    middle_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: str
    date_of_birth: Optional[date] = None
    role: UserRole 

class PersonCreate(PersonBase):
   
    id_card_series: str
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
    title: str              
    description: str        
    city: str               
    type: str               
    img: Optional[str] = None 
    area: Decimal
    price: Decimal
    room_count: int
    status: Optional[str] = "active"
    address_id: Optional[int] = None # Зробили необов'язковим для спрощення
    owner_id: int

class ApartmentCreate(ApartmentBase):
    pass

class ApartmentUpdate(BaseModel):
    title: Optional[str] = None
    area: Optional[Decimal] = None
    price: Optional[Decimal] = None
    room_count: Optional[int] = None
    status: Optional[str]=None

class ApartmentResponse(ApartmentBase):
    id: int
    class Config:
        from_attributes = True


class ContractBase(BaseModel):
    apartment_id: int
    owner_id: int
    
    start_date: date
    end_date: date
    price: Decimal
    total_sum: Decimal

class ContractCreate(ContractBase):
    pass # Бере всі поля з ContractBase (фронтенд відправляє саме їх)

class ContractStatusUpdate(BaseModel):
    status: str 

class ContractResponse(ContractBase):
    id: int
    tenant_id: int # Це поле додає сам бекенд з токена
    status: str    # Це поле теж додає бекенд ("в процесі")
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
        