from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

# 1. Додаємо імпорт users
from routers import properties, users 

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Real Estate Agency API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Підключаємо роутер користувачів
app.include_router(properties.router)
app.include_router(users.router) 

@app.get("/")
def root():
    return {"message": "API агенції нерухомості працює!"}