from fastapi import UploadFile, File,APIRouter
import shutil
import uuid

router = APIRouter(
    prefix="/api/images",   
    tags=["Images"]
)

@router.post("/upload-image/")
def upload_image(file: UploadFile = File(...)):
   
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    
    
    file_path = f"static/images/{unique_filename}"
    
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 4. Повертаємо фронтенду СПРАВЖНЄ посилання
    return {"img_url": f"http://localhost:8000/static/images/{unique_filename}"}