

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from database import get_db
import models, schemas
from routers.auth import get_current_user
from contract_generator import ContractGenerator

router = APIRouter(prefix="/api/contracts", tags=["Contracts"])


@router.post("/")
async def create_contract(
    payload: schemas.ContractCreate,
    db: Session = Depends(get_db),
    current_user: models.Person = Depends(get_current_user),
):
    # 1. Квартира
    apartment = db.query(models.Apartment).filter(
        models.Apartment.id == payload.apartment_id
    ).first()
    if not apartment:
        raise HTTPException(status_code=404, detail="Квартиру не знайдено")

    # ✅ Запитуємо через Person — уникаємо конфлікту поліморфізму
    owner = db.query(models.Person).filter(
        models.Person.id == payload.owner_id
    ).first()
    client = db.query(models.Person).filter(
        models.Person.id == payload.client_id
    ).first()

    if not owner or not client:
        raise HTTPException(status_code=404, detail="Власника або клієнта не знайдено")

    # 2. Зберігаємо контракт у БД
    new_contract = models.Contract(**payload.model_dump())
    db.add(new_contract)
    db.commit()
    db.refresh(new_contract)

    # 3. Дані для генератора документа
    # ✅ Використовуємо name/surname замість first_name/last_name
    data_for_doc = {
        "city":          apartment.city or "",
        "address":       f"{apartment.address.street}, {apartment.address.building}" if apartment.address else "",
        "landlord_name": f"{owner.name} {owner.surname}",
        "tenant_name":   f"{client.name} {client.surname}",
        "area":          str(apartment.area),
        "price":         str(payload.price),
        "total_sum":     str(payload.total_sum),
        "start_date":    str(payload.start_date),
        "end_date":      str(payload.end_date),
    }

    # 4. Генеруємо файл
    try:
        generator = ContractGenerator(data_for_doc)
        file_name = f"contract_{new_contract.id}.docx"
        file_path = os.path.abspath(f"temp_contracts/{file_name}")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        generator.generate_lease_contract(file_path)

        return FileResponse(
            path=file_path,
            filename=file_name,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    except Exception as e:
        print(f"Помилка генерації контракту: {e}")
        raise HTTPException(status_code=500, detail=f"Помилка при створенні файлу: {str(e)}")


@router.get("/my-contracts")
def get_my_contracts(
    db: Session = Depends(get_db),
    current_user: models.Person = Depends(get_current_user),
):
    return db.query(models.Contract).filter(
        (models.Contract.client_id == current_user.id) |
        (models.Contract.owner_id == current_user.id)
    ).all()


@router.patch("/{contract_id}/status")
def update_contract_status(
    contract_id: int,
    status_update: schemas.ContractStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.Person = Depends(get_current_user),
):
    if current_user.role != models.UserRole.owner and current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Тільки власник може змінювати статус")

    contract = db.query(models.Contract).filter(
        models.Contract.id == contract_id
    ).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Контракт не знайдено")

    contract.status = status_update.status
    db.commit()
    return {"message": f"Статус змінено на {status_update.status}"}