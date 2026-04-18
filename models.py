import enum
from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base

# 1. Створюємо перелік (Enum) для ролей
class UserRole(str, enum.Enum):
    admin = "admin"           # Адміністратор
    tenant = "tenant"         # Орендар (клієнт)
    landlord = "landlord"     # Орендодавець (власник)

class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    middle_name = Column(String(50))
    email = Column(String(100), unique=True)
    phone_number = Column(String(20), nullable=False, unique=True)
    date_of_birth = Column(Date)
    
    # 2. Додаємо поле role
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.tenant)

# Далі йдуть ваші інші таблиці без змін...
class Owner(Base):
    __tablename__ = 'owner'
    id = Column(Integer, ForeignKey('person.id', ondelete='CASCADE'), primary_key=True)
    person = relationship("Person")
    apartments = relationship("Apartment", back_populates="owner")

class Client(Base):
    __tablename__ = 'client'
    id = Column(Integer, ForeignKey('person.id', ondelete='CASCADE'), primary_key=True)
    id_card_series = Column(String(20), nullable=False, unique=True)
    person = relationship("Person")

class Realtor(Base):
    __tablename__ = 'realtor'
    id = Column(Integer, ForeignKey('person.id', ondelete='CASCADE'), primary_key=True)
    work_experience = Column(Integer, default=0)
    commission_rate = Column(Numeric(5, 2), nullable=False)
    person = relationship("Person")

class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True, index=True)
    street = Column(String(100), nullable=False)
    building = Column(String(20), nullable=False)
    apartment_number = Column(String(10), nullable=False)
    apartments = relationship("Apartment", back_populates="address")

class Apartment(Base):
    __tablename__ = 'apartment'
    id = Column(Integer, primary_key=True, index=True)
    area = Column(Numeric(10, 2), nullable=False)
    price = Column(Numeric(15, 0), nullable=False)
    room_count = Column(Integer, nullable=False)
    address_id = Column(Integer, ForeignKey('address.id', ondelete='RESTRICT'), nullable=False)
    owner_id = Column(Integer, ForeignKey('owner.id', ondelete='RESTRICT'), nullable=False)
    address = relationship("Address", back_populates="apartments")
    owner = relationship("Owner", back_populates="apartments")

class Contract(Base):
    __tablename__ = 'contract'
    id = Column(Integer, primary_key=True, index=True)
    apartment_id = Column(Integer, ForeignKey('apartment.id', ondelete='RESTRICT'), nullable=False)
    client_id = Column(Integer, ForeignKey('client.id', ondelete='RESTRICT'), nullable=False)
    realtor_id = Column(Integer, ForeignKey('realtor.id', ondelete='RESTRICT'), nullable=False)
    contract_date = Column(Date, nullable=False)
    total_sum = Column(Numeric(15, 2), nullable=False)