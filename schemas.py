from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date
from decimal import Decimal

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

class ApartmentResponse(ApartmentBase):
    id: int
    class Config:
        from_attributes = True