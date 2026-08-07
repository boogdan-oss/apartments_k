from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid, os, shutil
import models, schemas
from database import get_db
from routers.auth import get_current_user

router = APIRouter(
    prefix="/api/images",   
    tags=["Images"]
)

# Визначаємо шлях до папки для завантажень
UPLOAD_DIR = "static/images"

# @router.post("/upload-image/")
# def upload_image(file: UploadFile = File(...)):
   
#     file_extension = file.filename.split(".")[-1]
#     unique_filename = f"{uuid.uuid4()}.{file_extension}"
    
    
#     file_path = f"static/images/{unique_filename}"
    
    
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
        
#     # 4. Повертаємо фронтенду СПРАВЖНЄ посилання
#     return {"img_url": f"http://localhost:8000/static/images/{unique_filename}"}



@router.post("/upload-image/")
def upload_image(
    file: UploadFile = File(...),
    current_user: models.Person = Depends(get_current_user)
):
    """Завантажити одне фото — повертає URL."""
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    path = os.path.join(UPLOAD_DIR, filename)
 
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
 
    return {"img_url": f"http://localhost:8000/static/images/{filename}"}
 
 
@router.post("/apartment/{apartment_id}/images",
             response_model=List[schemas.ApartmentImageResponse])
def add_images_to_apartment(
    apartment_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: models.Person = Depends(get_current_user),
):
    """
    Завантажити декілька фото для квартири.
    ООП: Кожен файл → окремий ApartmentImage об'єкт (Композиція).
    Перше фото автоматично стає головним (is_main=True).
    """
    apartment = db.query(models.Apartment).filter(
        models.Apartment.id == apartment_id
    ).first()
    if not apartment:
        raise HTTPException(status_code=404, detail="Оголошення не знайдено")
    if apartment.owner_id != current_user.id and current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Немає прав")
 
    # Чи вже є фото — якщо ні, перше буде головним
    existing_count = len(apartment.images)
    saved = []
 
    for idx, file in enumerate(files):
        ext      = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        path     = os.path.join(UPLOAD_DIR, filename)
 
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
 
        # ООП: Створюємо окремий об'єкт для кожного фото
        img = models.ApartmentImage(
            apartment_id = apartment_id,
            url          = f"http://localhost:8000/static/images/{filename}",
            is_main      = (existing_count == 0 and idx == 0),  # перше — головне
        )
        db.add(img)
        saved.append(img)
 
    # Якщо головного фото ще немає — оновлюємо поле img у квартирі теж
    if existing_count == 0 and saved:
        apartment.img = saved[0].url
        db.add(apartment)
 
    db.commit()
    for img in saved:
        db.refresh(img)
 
    return saved
 
 
@router.delete("/apartment/{apartment_id}/images/{image_id}",
               status_code=204)
def delete_image(
    apartment_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    current_user: models.Person = Depends(get_current_user),
):
    """Видалити конкретне фото."""
    img = db.query(models.ApartmentImage).filter(
        models.ApartmentImage.id == image_id,
        models.ApartmentImage.apartment_id == apartment_id,
    ).first()
    if not img:
        raise HTTPException(status_code=404, detail="Фото не знайдено")
 
    apartment = db.query(models.Apartment).filter(
        models.Apartment.id == apartment_id).first()
    if apartment.owner_id != current_user.id and current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Немає прав")
 
    db.delete(img)
    db.commit()