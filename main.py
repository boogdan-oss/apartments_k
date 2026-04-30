from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import apartments,users,auth,contracts
from sqladmin import Admin
from admin import PersonAdmin,ApartmentAdmin,ContractAdmin
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Real Estate Agency API", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
admin = Admin(app, engine)
admin.add_view(PersonAdmin)
admin.add_view(ApartmentAdmin)
admin.add_view(ContractAdmin)

app.include_router(auth.router)
app.include_router(apartments.router)
app.include_router(users.router)
app.include_router(contracts.router)

@app.get("/")
def root():
    return {"message": "API працює! Складна архітектура підключена."}
@app.get("/api/health", tags=["Health Check"])
def health_check():
    return {
        "status": "ok", 
        "message": "Бекенд успішно з'єднано з фронтендом! "
    }









