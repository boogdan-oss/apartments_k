import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Ваш пароль та порт для локального Postgres (зазвичай порт 5432)
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://estate_agency_user:kYJgHM2xhHQ7IQcRzQ2liWYXqt6pR9S3@dpg-d7hl5ui8qa3s73enkk1g-a.oregon-postgres.render.com/estate_agency"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()