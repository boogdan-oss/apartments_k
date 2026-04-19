from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Ці назви мають ТОЧНО збігатися з тими, що у файлі .env
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Вказуємо Pydantic шукати змінні у файлі .env
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Створюємо об'єкт налаштувань, який будемо імпортувати в інші файли
settings = Settings()