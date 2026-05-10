from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from database import Base

# ООП: Параметричний поліморфізм — Generic типи
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


# -------------------------------------------------------
# ООП: Абстрактний базовий клас (ABC)
# Принцип: Абстракція — визначає інтерфейс без реалізації create().
# Принцип: Generics — один клас для будь-якої моделі.
# Принцип: Open/Closed — відкритий для розширення, закритий для змін.
# -------------------------------------------------------
class BaseRepository(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    def __init__(self, model: Type[ModelType]):
        # ООП: Інкапсуляція — модель як внутрішній стан об'єкта
        self.model = model

    # Конкретні методи — реалізовані тут, успадковуються дочірніми
    def get(self, db: Session, id: int) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def update(self, db: Session, db_obj: ModelType, schema: UpdateSchemaType) -> ModelType:
        data = schema.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> Optional[ModelType]:
        obj = self.get(db, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    # -------------------------------------------------------
    # ООП: Абстрактний метод — підкласи ЗОБОВ'ЯЗАНІ реалізувати.
    # Принцип: Поліморфізм — кожен підклас реалізує по-своєму.
    # -------------------------------------------------------
    @abstractmethod
    def create(self, db: Session, schema: CreateSchemaType) -> ModelType:
        """Кожен репозиторій реалізує create() по-своєму."""
        ...
