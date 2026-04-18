from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=False)
    telegram_link = Column(String(100), nullable=True) # Прямий контакт
    
    is_admin = Column(Boolean, default=False) # Для адмін-панелі
    
    properties = relationship("Property", back_populates="owner", cascade="all, delete-orphan")


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    city = Column(String(50), index=True, nullable=False) # Для пошуку
    address = Column(String(150), nullable=False)
    
    is_active = Column(Boolean, default=True) # Управління статусом (Активне / Здано)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User", back_populates="properties")
    photos = relationship("Photo", back_populates="property", cascade="all, delete-orphan")


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(255), nullable=False) # Шлях до файлу або посилання
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)

    property = relationship("Property", back_populates="photos")