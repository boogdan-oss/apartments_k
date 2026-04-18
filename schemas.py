from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal

# ==========================================
# PERSON (Особа / Користувач)
# ==========================================
class PersonBase(BaseModel):
    name: str
    surname: str
    middle_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: str
    date_of_birth: Optional[date] = None

class PersonCreate(PersonBase):
    pass

class PersonResponse(PersonBase):
    id: int

    class Config:
        from_attributes = True

# ==========================================
# ADDRESS (Адреса)
# ==========================================
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

# ==========================================
# APARTMENT (Апартаменти / Житло)
# ==========================================
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

# ==========================================
# CONTRACT (Договір)
# ==========================================
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