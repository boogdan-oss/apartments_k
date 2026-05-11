from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
import  auth, schemas, models
from auth import SECRET_KEY, ALGORITHM
import repositories
import jwt
from jwt.exceptions import InvalidTokenError

router = APIRouter(tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

@router.post("/api/auth/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Шукаємо користувача за email (у формі OAuth2 поле називається username, але ми передаємо email)
    user = repositories.get_by_email(db, email=form_data.username)
    
    # Перевіряємо чи є користувач і чи співпадає пароль
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильний email або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Створюємо токен
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не вдалося підтвердити облікові дані",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
        
    user = repositories.get_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user


@router.get("/api/auth/me", response_model=schemas.PersonResponse, summary="Отримати свій профіль")
def read_users_me(current_user: models.Person = Depends(get_current_user)):
    # Завдяки Depends(get_current_user), FastAPI сам дістане токен із заголовка,
    # розшифрує його, знайде користувача в базі і передасть у змінну current_user.
    # Якщо токена немає або він недійсний - FastAPI сам викине помилку 401.
    return current_user