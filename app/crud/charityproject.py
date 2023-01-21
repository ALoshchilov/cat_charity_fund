from typing import Optional

from fastapi.encoders import jsonable_encoder
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

    async def update(
        self,
        db_obj,
        obj_in,
        session: AsyncSession
    ):
        obj_data = jsonable_encoder(db_obj)        
        update_date = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_date:
                setattr(db_obj, field, update_date[field])
        if db_obj.full_amount == db_obj.invested_amount:
            db_obj = db_obj.close()
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj


charityproject_crud = CRUDCharityProject(CharityProject)
