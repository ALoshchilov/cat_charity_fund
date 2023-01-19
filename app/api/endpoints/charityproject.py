from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_full_amount_gt_invested, check_project_exists, check_project_has_donations,
    project_name_exists, check_project_not_close
)
from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud import charityproject_crud, donation_crud
from app.schemas.charityproject import CharityProjectCreate, CharityProjectDB, CharityProjectUpdate
from app.models import CharityProject, Donation
from app.services.services import invest_all_donations

router = APIRouter()

@router.get(
    '/',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_charityprojects(
    session: AsyncSession = Depends(get_async_session)
):
    charities = await charityproject_crud.get_multi(session)
    return charities

@router.get(
    '/opened_projects',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True,
)
async def foo(
    session: AsyncSession = Depends(get_async_session)
):
    # charities = await get_not_fully_invested_objects(
    #     model = CharityProject,
    #     session=session
    # )
    # await project_to_donate(session=session)
    await invest_all_donations(session=session)
    return []

@router.post(
    '/',
    response_model=CharityProjectDB,
)
async def create_charityproject(
    charityproject: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session)
):
    await project_name_exists(charityproject.name, session)
    new_project = await charityproject_crud.create(
        charityproject, session
    )
    return new_project

@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
)
async def delete_charityproject(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    project = await check_project_exists(project_id, session)
    await check_project_not_close(project.id, session)
    await check_project_has_donations(project.id, session)
    project = await charityproject_crud.remove(
        project, session
    )    
    return project

@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
)
async def patch_charityproject(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    project = await check_project_exists(project_id, session)
    await check_project_not_close(project.id, session)
    await check_full_amount_gt_invested(
        project.id, obj_in.full_amount, session
    )
    project = await charityproject_crud.update(
        project, obj_in, session
    )
    return project
