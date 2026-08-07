from sqladmin import  ModelView
import models 
from wtforms import SelectField

class PersonAdmin(ModelView, model=models.Person):
    # Які колонки показувати в списку?
    column_list = [models.Person.id, models.Person.name, models.Person.surname, models.Person.role]
    # По яких колонках можна шукати?
    column_searchable_list = [models.Person.name, models.Person.email]
    # Налаштування сортування за замовчуванням
    column_sortable_list = [models.Person.id]
    # Назва в меню (необов'язково)
    name = "Користувач"
    name_plural = "Користувачі"
    icon = "fa-solid fa-users"

# В'юшка для Оголошень (Apartment)
class ApartmentAdmin(ModelView, model=models.Apartment):
    # Колонки, які видно в загальній таблиці
    column_list = [models.Apartment.id, models.Apartment.title, models.Apartment.price, models.Apartment.status]
    
    # Налаштування пошуку
    column_searchable_list = [models.Apartment.title]
    
    name = "Оголошення"
    name_plural = "Оголошення"
    icon = "fa-solid fa-building"

    # ДОДАЄМО ЦЕ: Налаштування форми редагування
    form_widget_args = {
        "title": {"readonly": True},
        "description": {"readonly": True},
        "city": {"readonly": True},
        "type": {"readonly": True},
        "area": {"readonly": True},
        "price": {"readonly": True},
        "room_count": {"readonly": True},
        "owner_id": {"readonly": True},
        "img":{"readonly": True},
        "telegram":{"readonly":True}
        
    }
    form_overrides = {
        "status": SelectField
    }
    
    # 2. Вказуємо, які саме варіанти будуть у списку
    form_args = {
        "status": {
            "choices": [
                ("pending", "На перевірці (Pending)"),
                ("active", "Схвалено (Active)"),
                ("banned", "Заблоковано (Banned)")
            ]
        }
    }

# admin.py

class ReviewAdmin(ModelView, model=models.Review):
    column_list = [
        models.Review.id, 
        models.Review.author_id, 
        models.Review.apartment_id, 
        models.Review.status, 
        models.Review.created_at
    ]
    
    column_searchable_list = [models.Review.text]
    
    name = "Відгук"
    name_plural = "Відгуки"
    icon = "fa-solid fa-comment-dots"

    # Налаштування форми редагування
    form_overrides = {
        "status": SelectField
    }
    
    form_args = {
        "status": {
            "choices": [
                ("active", "Активний (Опубліковано)"),
                ("banned", "Заблокований (Приховано)")
            ]
        }
    }
    
    # Робимо текст відгуку та посилання на автора тільки для читання, 
    # щоб модератор міг змінити лише статус
    form_widget_args = {
        "text": {"readonly": True},
        "author_id": {"readonly": True},
        "apartment_id": {"readonly": True},
        "created_at": {"readonly": True}
    }
