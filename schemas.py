from pydantic import BaseModel
from typing import Optional,List
from datetime import date
from decimal import Decimal
from models import UserRole
from datetime import datetime

#валідація.структура,репка і модулі

class PersonBase(BaseModel):
    name: str
    surname: str
    middle_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: str
    id_card_series: str
    date_of_birth: Optional[date] = None
    role: UserRole 

class PersonCreate(PersonBase):
   
    
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
    id:int#delete
    street: str
    building: str
    apartment_number: str

class AddressCreate(AddressBase):
    pass

class AddressResponse(AddressBase):
    id: int
    class Config:
        from_attributes = True


class ApartmentBase(BaseModel):
    title: str              
    description: str        
    city: str               
    type: str               
    img: Optional[str] = None 
    area: Decimal
    price: Decimal
    room_count: int
    address_id: Optional[int] = None 
    telegram: Optional[str] = None
   

class ApartmentCreate(ApartmentBase):
    pass

class ApartmentImageResponse(BaseModel):
    id: int
    url: str
    is_main: bool
    class Config:
        from_attributes = True

class ApartmentUpdate(BaseModel):
    title: Optional[str] = None
    area: Optional[Decimal] = None
    price: Optional[Decimal] = None
    room_count: Optional[int] = None
    status: Optional[str]=None

class ApartmentResponse(ApartmentBase):
    id: int
    owner_id: int
    images: List[ApartmentImageResponse] = []
    telegram: Optional[str] = None
    owner: Optional[PersonResponse] = None
    class Config:
        from_attributes = True


class Contract(BaseModel):
    apartment_id: int
    owner_id: int
    client_id:int
    start_date: date
    end_date: date
    price: float
    total_sum: float

    class Config:
        from_attributes = True

class ContractCreate(Contract):
    pass 

class ContractStatusUpdate(BaseModel):
    status: str 

class ContractResponse(Contract):
    id: int
    owner_id: int 
    status: str    
    
    class Config:
        from_attributes = True



class ReviewCreate(BaseModel):
    text: str  # тільки текст — автор і квартира беруться з токена і URL
 
 
class ReviewResponse(BaseModel):
    id: int
    text: str
    created_at: datetime
   
    author_name: str
    author_surname: str
 
    class Config:
        from_attributes = True        

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
        