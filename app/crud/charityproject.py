from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject


class CRUDCharityProject(CRUDBase):

    async def get_project_id_by_name(
        name,
        project_name: str,
        session: AsyncSession,
    ) -> Optional[int]:
        db_project_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name
            )
        )
        return db_project_id.scalars().first()

    async def get_first_opened_project(
        session: AsyncSession,
    ) -> Optional[CharityProject]:
        db_project = await session.execute(
            select(CharityProject.id).where(
                CharityProject.fully_invested == 0,
            )
        )
        return db_project.scalars().first()

    async def transfer_donation(
        project_id: int,
        amount: int,
        session: AsyncSession,
    ) -> int:
        project = await charityproject_crud.get_first_opened_project(session)
        left_amount = project.full_amount - project.invested_amount
        if amount < left_amount:
            setattr(
                project, 'invested_amount', project.invested_amount + amount
            )
        else:
            setattr(
                project, 'invested_amount', project.full_amount
            )
            setattr(
                project, 'fully_invested', True
            )
        session.add(project)
        await session.commit()
        await session.refresh(project)
        return project.full_amount - amount


charityproject_crud = CRUDCharityProject(CharityProject)
