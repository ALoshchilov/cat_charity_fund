from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud import charityproject_crud, donation_crud
from app.models import User
from app.schemas.donation import DonationCreate, DonationDB
from app.services.services import invest_all_donations


EXCLUDED_FIELDS = ('user_id', 'invested_amount', 'fully_invested', 'close_date',)


router = APIRouter()

@router.get(
    '/',
    response_model=list[DonationDB],
    dependencies=[Depends(current_superuser)],
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
    response_model_exclude={*EXCLUDED_FIELDS}
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
    response_model_exclude_none=True,
    response_model_exclude={*EXCLUDED_FIELDS}
)
async def post_donation(
    donation: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):    
    donation = await donation_crud.create(
        donation, session, user
    )
    await invest_all_donations(session=session)
    await session.refresh(donation)
    return donation
