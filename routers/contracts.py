from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from routers.auth import get_current_user # Ваш імпорт перевірки токена

router = APIRouter(prefix="/api/contracts", tags=["Contracts"])

# 1. СТВОРЕННЯ ЗАЯВКИ (ОРЕНДАР)
@router.post("/")
def create_contract(contract: schemas.ContractCreate, db: Session = Depends(get_db), current_user: models.Person = Depends(get_current_user)):
    if current_user.role != "tenant":
        raise HTTPException(status_code=403, detail="Тільки орендар може створювати заявку")

    new_contract = models.Contract(
        apartment_id=contract.apartment_id,
        client_id=current_user.id, 
        total_sum=contract.total_sum,
        status="pending"
    )
    db.add(new_contract)
    db.commit()
    return {"message": "Заявку успішно відправлено!"}

# 2. ОТРИМАННЯ ЗАЯВОК ДЛЯ ВЛАСНИКА
@router.get("/my-requests")
def get_owner_requests(db: Session = Depends(get_db), current_user: models.Person = Depends(get_current_user)):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Тільки власник має доступ до цього списку")
    
    # Шукаємо всі контракти на квартири, які належать цьому власнику
    requests = db.query(models.Contract).join(models.Apartment).filter(models.Apartment.owner_id == current_user.id).all()
    return requests

# 3. ПІДТВЕРДЖЕННЯ / ВІДМОВА (ВЛАСНИК)
@router.patch("/{contract_id}/status")
def update_contract_status(contract_id: int, status_update: schemas.ContractStatusUpdate, db: Session = Depends(get_db), current_user: models.Person = Depends(get_current_user)):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Тільки власник може змінювати статус")

    contract = db.query(models.Contract).filter(models.Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Контракт не знайдено")
        
    contract.status = status_update.status
    db.commit()
    return {"message": f"Статус змінено на {status_update.status}"}