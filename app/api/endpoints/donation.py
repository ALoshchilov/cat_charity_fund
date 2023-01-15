from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud import charityproject_crud, donation_crud
from app.models import User
from app.schemas.donation import DonationCreate, DonationDB

router = APIRouter()

@router.get(
    '/',
    response_model=list[DonationDB],
    response_model_exclude_none=True,
)
async def get_donations(
    session: AsyncSession = Depends(get_async_session)
):
    donations = await donation_crud.get_multi(session)
    return donations

@router.get(
    '/my',
    response_model=list[DonationDB],
    response_model_exclude={'user_id'}
)
async def get_my_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):
    my_donations = await donation_crud.get_by_user(
        session=session, user=user
    )
    return my_donations

@router.post(
    '/',
    response_model=DonationDB,
)
async def post_donation(
    donation: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):
    donation = await donation_crud.create(
        donation, session, user
    )
    return donation
