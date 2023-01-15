import os
from typing import Optional

from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):    
    app_author: str
    app_title: str = 'QRKot'
    app_description: str
    database_url: str
    path: str
    secret: str = 'SECRET'
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None

    class Config:
        env_file = '.env'

settings = Settings()
