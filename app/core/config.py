from typing import Optional

from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    app_author: str = 'Loschilov Aleksandr'
    app_title: str = 'QRKot'
    app_description: str = (
        'Проект API сервиса для благотворительной поддержки котиков =^.^='
    )
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    secret: str = 'SECRET'
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None

    class Config:
        env_file = '.env'


settings = Settings()
