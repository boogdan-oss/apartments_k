# # import enum
# # from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Enum as SQLEnum
# # from sqlalchemy.orm import relationship
# # from database import Base


# # class UserRole(str, enum.Enum):
# #     admin = "admin"           # Адміністратор 
# #     client="client"    # Орендодавець (власник)
    
# # class ApartmentStatus(str,enum.Enum):
# #     active="active"
# #     pending="pending"
# #     banned="banned"    

# # class Person(Base):
# #     __tablename__ = 'person'
# #     id = Column(Integer, primary_key=True, index=True)
# #     name = Column(String(50), nullable=False)
# #     surname = Column(String(50), nullable=False)
# #     email = Column(String(100), unique=True,nullable=False)
# #     hashed_password = Column(String(255), nullable=False)
# #     phone_number = Column(String(20), nullable=False, unique=True)
# #     date_of_birth = Column(Date)
# #     role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.client)

# # # Далі йдуть ваші інші таблиці без змін...
# # class Owner(Base):
# #     __tablename__ = 'owner'
# #     id = Column(Integer, ForeignKey('person.id', ondelete='CASCADE'), primary_key=True)
# #     person = relationship("Person")
# #     apartments = relationship("Apartment", back_populates="owner")

# # class Client(Base):
# #     __tablename__ = 'client'
# #     id = Column(Integer, ForeignKey('person.id', ondelete='CASCADE'), primary_key=True)
# #     id_card_series = Column(String(20), nullable=False, unique=True)
# #     person = relationship("Person")



# # class Address(Base):
# #     __tablename__ = 'address'
# #     id = Column(Integer, primary_key=True, index=True)
# #     street = Column(String(100), nullable=False)
# #     building = Column(String(20), nullable=False)
# #     apartment_number = Column(String(10), nullable=False)
# #     apartments = relationship("Apartment", back_populates="address")

# # class Favorite(Base):
# #     __tablename__ = "favorites"

# #     id = Column(Integer, primary_key=True, index=True)
# #     user_id = Column(Integer, ForeignKey("person.id", ondelete="CASCADE")) 
# #     apartment_id = Column(Integer, ForeignKey("apartment.id", ondelete="CASCADE"))
    
# #     # Зв'язки, щоб легко діставати дані
# #     user = relationship("Person") 
# #     apartment = relationship("Apartment")



# # class Apartment(Base):
# #     __tablename__ = 'apartment'
# #     id = Column(Integer, primary_key=True, index=True)
# #     title=Column(String,nullable=False)
# #     description=Column(String)
# #     city=Column(String)
# #     type=Column(String,nullable=False)
# #     img=Column(String,nullable=True)
# #     area = Column(Numeric(10, 2), nullable=False)
# #     price = Column(Numeric(15, 0), nullable=False)
# #     room_count = Column(Integer, nullable=False)
# #     status = Column(String, default="active")
# #     address_id = Column(Integer, ForeignKey('address.id', ondelete='RESTRICT'), nullable=False)
# #     owner_id = Column(Integer, ForeignKey('owner.id', ondelete='RESTRICT'), nullable=False)
# #     address = relationship("Address", back_populates="apartments")
# #     owner = relationship("Owner", back_populates="apartments")




# # class Contract(Base):
# #     __tablename__ = "contract"
# #     id = Column(Integer, primary_key=True, index=True)
# #     apartment_id = Column(Integer, ForeignKey("apartment.id"))
# #     owner_id = Column(Integer, ForeignKey("person.id")) 
# #     client_id = Column(Integer, ForeignKey("person.id"))
# #     start_date = Column(Date, nullable=False)
# #     end_date = Column(Date, nullable=False)
# #     price = Column(Numeric(15), nullable=False)
# #     status = Column(String, default="в процесі") 
# #     apartment = relationship("Apartment")
# #     owner = relationship("Person", foreign_keys=[owner_id])
# #     client = relationship("Person", foreign_keys=[client_id])

# import enum
# from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Enum as SQLEnum
# from sqlalchemy.orm import relationship
# from database import Base


# class UserRole(str, enum.Enum):
#     admin = "admin"
#     client = "client"
#     owner="owner"


# class ApartmentStatus(str, enum.Enum):
#     active = "active"
#     pending = "pending"
#     banned = "banned"


# class Person(Base):
#     __tablename__ = 'person'

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(50), nullable=False)
#     surname = Column(String(50), nullable=False)
#     email = Column(String(100), unique=True, nullable=False)
#     id_card_series=Column(String,unique=True,nullable=True)
#     hashed_password = Column(String(255), nullable=False)
#     phone_number = Column(String(20), nullable=False, unique=True)
#     date_of_birth = Column(Date)
#     role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.client)


# class Address(Base):
#     __tablename__ = 'address'

#     id = Column(Integer, primary_key=True, index=True)
#     street = Column(String(100), nullable=False)
#     building = Column(String(20), nullable=False)
#     apartment_number = Column(String(10), nullable=False)
#     apartments = relationship("Apartment", back_populates="address")


# class Apartment(Base):
#     __tablename__ = 'apartment'

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String(200), nullable=False)
#     description = Column(String(2000))
#     city = Column(String(100))
#     type = Column(String(50), nullable=False)
#     img = Column(String(500), nullable=True)
#     area = Column(Numeric(10, 2), nullable=False)
#     price = Column(Numeric(15, 0), nullable=False)
#     room_count = Column(Integer, nullable=False)
#     status = Column(String(20), default="active")
#     address_id = Column(Integer, ForeignKey('address.id', ondelete='RESTRICT'), nullable=False)
#     # ✅ Було ForeignKey('owner.id') → тепер напряму ForeignKey('person.id')
#     owner_id = Column(Integer, ForeignKey('person.id', ondelete='RESTRICT'), nullable=False)

#     address = relationship("Address", back_populates="apartments")
#     owner = relationship("Person", foreign_keys=[owner_id])


# class Favorite(Base):
#     __tablename__ = 'favorites'

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey('person.id', ondelete='CASCADE'), nullable=False)
#     apartment_id = Column(Integer, ForeignKey('apartment.id', ondelete='CASCADE'), nullable=False)

#     user = relationship("Person")
#     apartment = relationship("Apartment")


# class Contract(Base):
#     __tablename__ = 'contract'

#     id = Column(Integer, primary_key=True, index=True)
#     apartment_id = Column(Integer, ForeignKey('apartment.id'), nullable=False)
#     owner_id = Column(Integer, ForeignKey('person.id'), nullable=False)
#     client_id = Column(Integer, ForeignKey('person.id'), nullable=False)
#     start_date = Column(Date, nullable=False)
#     end_date = Column(Date, nullable=False)
#     price = Column(Numeric(15, 2), nullable=False)
#     status = Column(String(50), default="в процесі")

#     apartment = relationship("Apartment")
#     owner = relationship("Person", foreign_keys=[owner_id])
#     client = relationship("Person", foreign_keys=[client_id])


# class Owner(Base):
#     __tablename__ = 'owner'
#     id = Column(Integer, ForeignKey('person.id', ondelete='CASCADE'), primary_key=True)
#     person = relationship("Person")
   

# class Client(Base):
#     __tablename__ = 'client'
#     id = Column(Integer, ForeignKey('person.id', ondelete='CASCADE'), primary_key=True)
#     id_card_series = Column(String(20), nullable=False, unique=True)
#     person = relationship("Person")



import enum
from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base


# -------------------------------------------------------
# ENUMS
# -------------------------------------------------------

class UserRole(str, enum.Enum):
    admin  = "admin"
    client = "client"
    owner  = "owner"

class ApartmentStatus(str, enum.Enum):
    active  = "active"
    pending = "pending"
    banned  = "banned"


# -------------------------------------------------------
# ООП: БАЗОВИЙ КЛАС — Person
# Принцип: Інкапсуляція — всі спільні поля зібрані тут.
# Принцип: Наслідування — Owner і Client наслідують Person.
# Стратегія: Joined Table Inheritance (окремі таблиці).
# -------------------------------------------------------
class Person(Base):
    __tablename__ = "person"

    id             = Column(Integer, primary_key=True, index=True)
    name           = Column(String(50),  nullable=False)
    surname        = Column(String(50),  nullable=False)
    email          = Column(String(100), unique=True, nullable=False)
    hashed_password= Column(String(255), nullable=False)
    phone_number   = Column(String(20),  unique=True, nullable=False)
    date_of_birth  = Column(Date, nullable=True)
    id_card_series = Column(String(50),  unique=True, nullable=True)

    # Дискримінатор поліморфізму: SQLAlchemy дивиться на це поле
    # і вирішує який підклас (Owner / Client / Person) повернути.
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.client)

    __mapper_args__ = {
        "polymorphic_on":       role,
        "polymorphic_identity": UserRole.admin,  # Person без підкласу = admin
    }


# -------------------------------------------------------
# ООП: ДОЧІРНІЙ КЛАС — Owner
# Принцип: Наслідування — отримує всі поля Person.
# Принцип: Розширення — додає зв'язок з квартирами.
# -------------------------------------------------------
class Owner(Person):
    __tablename__ = "owner"

    # id = той самий ідентифікатор що й у Person (one-to-one)
    id = Column(Integer, ForeignKey("person.id", ondelete="CASCADE"), primary_key=True)

    # Специфічний зв'язок тільки у власника
    apartments = relationship("Apartment", foreign_keys="Apartment.owner_id",
                              back_populates="owner")

    __mapper_args__ = {
        "polymorphic_identity": UserRole.owner,
    }


# -------------------------------------------------------
# ООП: ДОЧІРНІЙ КЛАС — Client
# Принцип: Наслідування + Розширення — додає id_card_series_extra.
# -------------------------------------------------------
class Client(Person):
    __tablename__ = "client"

    id = Column(Integer, ForeignKey("person.id", ondelete="CASCADE"), primary_key=True)

    # Поле специфічне тільки для орендаря
    id_card_series_extra = Column(String(20), unique=True, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": UserRole.client,
    }


# -------------------------------------------------------
# Інші моделі (без змін у структурі)
# -------------------------------------------------------

class Address(Base):
    __tablename__ = "address"

    id               = Column(Integer, primary_key=True, index=True)
    street           = Column(String(100), nullable=False)
    building         = Column(String(20),  nullable=False)
    apartment_number = Column(String(10),  nullable=False)
    apartments       = relationship("Apartment", back_populates="address")


class Apartment(Base):
    __tablename__ = "apartment"

    id         = Column(Integer, primary_key=True, index=True)
    title      = Column(String(200), nullable=False)
    description= Column(String(2000))
    city       = Column(String(100))
    type       = Column(String(50),  nullable=False)
    img        = Column(String(500),  nullable=True)
    area       = Column(Numeric(10, 2), nullable=False)
    price      = Column(Numeric(15, 0), nullable=False)
    room_count = Column(Integer, nullable=False)
    status     = Column(String(20), default="active")
    address_id = Column(Integer, ForeignKey("address.id", ondelete="RESTRICT"), nullable=False)
    owner_id   = Column(Integer, ForeignKey("person.id", ondelete="RESTRICT"),  nullable=False)

    address = relationship("Address", back_populates="apartments")
    owner   = relationship("Owner", foreign_keys=[owner_id], back_populates="apartments")


class Favorite(Base):
    __tablename__ = "favorites"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("person.id",    ondelete="CASCADE"), nullable=False)
    apartment_id = Column(Integer, ForeignKey("apartment.id", ondelete="CASCADE"), nullable=False)

    user      = relationship("Person")
    apartment = relationship("Apartment")


class Contract(Base):
    __tablename__ = "contract"

    id           = Column(Integer, primary_key=True, index=True)
    apartment_id = Column(Integer, ForeignKey("apartment.id"), nullable=False)
    owner_id     = Column(Integer, ForeignKey("person.id"),    nullable=False)
    client_id    = Column(Integer, ForeignKey("person.id"),    nullable=False)
    start_date   = Column(Date, nullable=False)
    end_date     = Column(Date, nullable=False)
    price        = Column(Numeric(15, 2), nullable=False)
    status       = Column(String(50), default="в процесі")

    apartment = relationship("Apartment")
    owner     = relationship("Person", foreign_keys=[owner_id])
    client    = relationship("Person", foreign_keys=[client_id])
