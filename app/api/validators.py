from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import charityproject_crud
from app.core.messages import (
    DELETE_INVESTED_PROJECT_DISALLOWED, EDIT_CLOSED_PROJECT_DISALLOWED,
    FULL_AMOUNT_MUST_BE_GRATER_INVESTED, PROJECT_DOES_NOT_EXIST,
    PROJECT_NAME_IS_BUSY
)


async def project_name_exists(
    name: str,
    session: AsyncSession,
):
    project_id = await charityproject_crud.get_project_id_by_name(
        name, session
    )
    if project_id is not None:
        raise HTTPException(
            status_code=400,
            detail=PROJECT_NAME_IS_BUSY,
        )


async def check_project_exists(
    project_id: str,
    session: AsyncSession,
):
    project = await charityproject_crud.get(project_id, session)
    if project is None:
        raise HTTPException(
            status_code=404,
            detail=PROJECT_DOES_NOT_EXIST.format(project_id=project_id),
        )
    return project


async def check_project_not_close(
    id: int,
    session: AsyncSession,
):
    project = await charityproject_crud.get(id, session)
    if project and project.fully_invested:
        raise HTTPException(
            status_code=400,
            detail=EDIT_CLOSED_PROJECT_DISALLOWED,
        )


async def check_project_has_donations(
    id: int,
    session: AsyncSession,
):
    project = await charityproject_crud.get(id, session)
    if project and project.invested_amount > 0:
        raise HTTPException(
            status_code=400,
            detail=DELETE_INVESTED_PROJECT_DISALLOWED,
        )


async def check_full_amount_gt_invested(
    id: int,
    new_full_amount,
    session: AsyncSession,
):
    project = await charityproject_crud.get(id, session)
    if project and new_full_amount < project.invested_amount:
        raise HTTPException(
            status_code=422,
            detail=FULL_AMOUNT_MUST_BE_GRATER_INVESTED,
        )
