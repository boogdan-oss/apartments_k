from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from routers.auth import get_current_user # Ваш імпорт перевірки токена

router = APIRouter(prefix="/api/contracts", tags=["Contracts"])

# 1. СТВОРЕННЯ ЗАЯВКИ (ОРЕНДАР)
@router.post("/")
def create_contract(
    contract_data: schemas.ContractCreate, 
    db: Session = Depends(get_db),
    current_user: models.Person = Depends(get_current_user)
):
    # Створюємо запис контракту
    new_contract = models.Contract(
        apartment_id=contract_data.apartment_id,
        owner_id=contract_data.owner_id,
        tenant_id=current_user.id,
        start_date=contract_data.start_date,
        end_date=contract_data.end_date,
        price=contract_data.price,
        status="в процесі"
    )
    db.add(new_contract)
    db.commit()
    return {"message": "Контракт відправлено власнику"}

@router.get("/my-contracts")
def get_my_contracts(db: Session = Depends(get_db), current_user: models.Person = Depends(get_current_user)):
    # Повертає контракти, де користувач або орендар, або власник
    return db.query(models.Contract).filter(
        (models.Contract.tenant_id == current_user.id) | 
        (models.Contract.owner_id == current_user.id)
    ).all()
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