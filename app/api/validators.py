from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.user import current_user
from app.crud import charityproject_crud, donation_crud

async def project_name_exists(
    name: str,
    session: AsyncSession,
):
    project_id = await charityproject_crud.get_project_id_by_name(
        name, session
    )
    if project_id is not None:
        raise HTTPException(
            status_code=422,
            detail='Проект сбора пожертвований с таким именем уже существует!',
        )

async def check_project_exists(
    project_id: str,
    session: AsyncSession,
):
    project= await charityproject_crud.get(project_id, session)
    if project is None:
        raise HTTPException(
            status_code=404,
            detail=f'Проект сбора пожертвований с указанным {project_id} не существует!',
        )
    return project
    

async def check_project_not_close(
    id: int,
    session: AsyncSession,
):
    project = await charityproject_crud.get(id, session)
    if project and project.fully_invested:
        raise HTTPException(
            status_code=422,
            detail='Нельзя изменять закрытые проекты сбора пожертвований!',
        )

async def check_project_has_donations(
    id: int,
    session: AsyncSession,
):
    project = await charityproject_crud.get(id, session)
    if project and not project.fully_invested and project.invested_amount > 0:
        raise HTTPException(
            status_code=422,
            detail='Нельзя изменить проект, в него перечислены пожертвования',
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
            detail='Нельзя задать целевое значение сборов {} меньше, чем уже инвестировано {}',
        )
