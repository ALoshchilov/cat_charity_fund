from fastapi import APIRouter

from app.api.endpoints import (
    charityproject_router, donation_router, user_router
)


main_router = APIRouter()
main_router.include_router(
    charityproject_router,
    prefix='/charity_project',
    tags=['charity_project']
)
main_router.include_router(
    donation_router,
    prefix='/donation',
    tags=['donation']
)
main_router.include_router(user_router)
