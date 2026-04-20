from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

# Підключаємо роутер квартир
from routers import apartments,users,auth



# Цей рядок створить їх наново з новими колонками
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Real Estate Agency API", version="2.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(apartments.router)
app.include_router(users.router)
@app.get("/")
def root():
    return {"message": "API працює! Складна архітектура підключена."}
@app.get("/api/health", tags=["Health Check"])
def health_check():
    return {
        "status": "ok", 
        "message": "Бекенд успішно з'єднано з фронтендом! 🚀"
    }