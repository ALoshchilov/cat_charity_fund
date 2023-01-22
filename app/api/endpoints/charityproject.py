from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_full_amount_gt_invested, check_project_exists,
    check_project_has_donations, project_name_exists, check_project_not_close
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud import charityproject_crud, donation_crud
from app.schemas.charityproject import (
    CharityProjectCreate, CharityProjectDB, CharityProjectUpdate
)
from app.services.investments import distribute_amounts

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
    '/get_not_fully_invested_objects',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_opened_charityprojects(
    session: AsyncSession = Depends(get_async_session)
):
    projects = await charityproject_crud.get_not_closed(session)
    donations = await donation_crud.get_not_closed(session)
    updated_donations, updated_projects = distribute_amounts(
        donations=donations, projects=projects
    )
    session.add_all(updated_donations)
    session.add_all(updated_projects)
    await session.commit()


@router.post(
    '/',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
    response_model_exclude_none=True,
)
async def create_charityproject(
    charityproject: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session)
):
    await project_name_exists(charityproject.name, session)
    new_project = await charityproject_crud.create(
        charityproject, session, commited=True
    )
    projects = await charityproject_crud.get_not_closed(session)
    donations = await donation_crud.get_not_closed(session)
    updated_donations, updated_projects = distribute_amounts(
        donations=donations, projects=projects
    )
    session.add_all(updated_donations)
    session.add_all(updated_projects)
    await session.commit()
    await session.refresh(new_project)
    return new_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def delete_charityproject(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    project = await check_project_exists(project_id, session)
    await check_project_has_donations(project.id, session)
    project = await charityproject_crud.remove(
        project, session
    )
    return project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def patch_charityproject(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    project = await check_project_exists(project_id, session)

    await check_project_not_close(project.id, session)
    if obj_in.name is not None:
        await project_name_exists(obj_in.name, session)
    if obj_in.full_amount is not None:
        await check_full_amount_gt_invested(
            project.id, obj_in.full_amount, session
        )
    project = await charityproject_crud.update(
        project, obj_in, session
    )
    return project
