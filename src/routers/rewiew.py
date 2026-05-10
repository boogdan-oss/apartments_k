from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from database import get_db
from routers.auth import get_current_user

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


@router.get("/{apartment_id}", response_model=List[schemas.ReviewResponse])
def get_reviews(apartment_id: int, db: Session = Depends(get_db)):
    """Отримати всі відгуки для оголошення."""
    reviews = (
        db.query(models.Review)
        .filter(models.Review.apartment_id == apartment_id,models.Review.status=="active")
        .order_by(models.Review.created_at.desc())
        .all()
    )
    # Формуємо відповідь вручну — додаємо ім'я автора
    return [
        schemas.ReviewResponse(
            id=r.id,
            text=r.text,
            created_at=r.created_at,
            author_name=r.author.name,
            author_surname=r.author.surname,
        )
        for r in reviews
    ]


@router.post("/{apartment_id}", response_model=schemas.ReviewResponse,
             status_code=status.HTTP_201_CREATED)
def create_review(
    apartment_id: int,
    review_data: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    current_user: models.Person = Depends(get_current_user),
):
    """Додати відгук до оголошення."""
    # Перевіряємо що квартира існує
    apartment = db.query(models.Apartment).filter(
        models.Apartment.id == apartment_id
    ).first()
    if not apartment:
        raise HTTPException(status_code=404, detail="Оголошення не знайдено")

    # Власник не може писати відгук на своє оголошення
    if apartment.owner_id == current_user.id:
        raise HTTPException(status_code=403, detail="Не можна писати відгук на власне оголошення")

    review = models.Review(
        apartment_id=apartment_id,
        author_id=current_user.id,
        text=review_data.text,
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    return schemas.ReviewResponse(
        id=review.id,
        text=review.text,
        created_at=review.created_at,
        author_name=current_user.name,
        author_surname=current_user.surname,
    )


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: models.Person = Depends(get_current_user),
):
    """Видалити відгук (тільки автор або адмін)."""
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Відгук не знайдено")

    if review.author_id != current_user.id and current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Немає прав на видалення")

    db.delete(review)
    db.commit()