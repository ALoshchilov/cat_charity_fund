from fastapi import Depends
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.user import current_user
from app.crud.base import CRUDBase
from app.models import Donation, User

class CRUDDonation(CRUDBase):

    async def get_by_user(
        self,
        session: AsyncSession,
        user: User = Depends(current_user)
    ) -> list[Donation]:
        my_donations = await session.execute(
            select(Donation).where(
                Donation.user_id == user.id
            )
        )
        return my_donations.scalars().all()

donation_crud = CRUDDonation(Donation)
