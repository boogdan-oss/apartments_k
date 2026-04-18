from fastapi import FastAPI
from database import engine, Base
from routers import apartments
# from routers import contracts # Підключите, коли створите роутер для договорів

# Створюємо таблиці в базі даних, якщо їх там ще немає
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Real Estate Agency API",
    description="Документація (Swagger) для курсового проєкту агенції нерухомості",
    version="1.0.0"
)

# Підключаємо роутери
app.include_router(apartments.router)
#app.include_router(contracts.router)


@app.get("/")
def root():
    return {"message": "API агенції нерухомості працює! Перейдіть на /docs для перегляду Swagger."}