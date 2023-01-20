from fastapi import FastAPI

from app.api.routers import main_router
from app.core.config import settings

app = FastAPI(
    description=settings.app_description,
    title=settings.app_title
)

app.include_router(main_router)
