from datetime import datetime
from typing import Union

from sqlalchemy import asc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.models import CharityProject, Donation


async def get_not_fully_invested_objects(
    model: Union[CharityProject, Donation],
    session: AsyncSession
):
    db_objects = await session.execute(
        select(model).where(
            model.fully_invested == False
        ).order_by(asc(model.id))
    )
    return db_objects.scalars().all()

async def get_total_not_invested(
    model: Union[CharityProject, Donation],
    session: AsyncSession
):  
    query = select(
        func.sum(model.full_amount) - 
        func.sum(model.invested_amount),
    ).where(
        model.fully_invested == False
    )
    amounts = await session.execute(query)
    return amounts.scalars().first()

async def close_object(
    object: Union[CharityProject, Donation],
    session: AsyncSession
):
    object.fully_invested = True
    object.invested_amount = object.full_amount
    object.close_date = datetime.now()


async def close_all_objects(
    model: Union[CharityProject, Donation],
    session: AsyncSession
):
    query = (
        update(model).
        where(model.fully_invested == False).
        values(
            fully_invested = True,
            invested_amount = model.full_amount,
            close_date = datetime.now()
        )
    )
    await session.execute(query)


async def invest_all_donations(
    session: AsyncSession
):
    total_unused_amount = await get_total_not_invested(
        Donation, session
    ) or 0
    total_need_amount = await get_total_not_invested(
        CharityProject, session
    ) or 0    
    print(f'total unused: {total_unused_amount}')
    print(f'total need: {total_need_amount}')
    if total_unused_amount == total_need_amount:
        await close_all_objects(CharityProject,session)
        await close_all_objects(Donation,session)
        await session.commit()
        return None    
    if total_unused_amount < total_need_amount:
        projects = await get_not_fully_invested_objects(
            CharityProject, session
        )
        left = total_unused_amount
        for project in projects:
            need = project.full_amount - project.invested_amount
            left = left - need
            print(f'left: {left}, need: {need}')
            if left > 0:
                print(f'Проект {project.name}. Зачислено: {project.full_amount}')
                await close_object(project, session)
                continue
            if not project.invested_amount:
                amount = project.full_amount - abs(left)
            else:
                amount = project.invested_amount + total_unused_amount
            setattr(project, 'invested_amount', amount)
            await close_all_objects(Donation,session)
            print(f'Проект {project.name}. Зачислено: {amount}')
            break        
        await session.commit()
        return None
    if total_need_amount > total_unused_amount:
        donations = await get_not_fully_invested_objects(
            Donation, session
        )
        left = total_need_amount
        for donation in donations:
            available = donation.full_amount - donation.invested_amount
            left = left - available
            print(f'left: {left}, available: {available}')
            if left > 0:
                print(f'Из доната {donation.id}. Зачислено: {donation.full_amount}')
                await close_object(donation, session)
                continue
            if not donation.invested_amount:
                amount = donation.full_amount - abs(left)
            else:
                amount = donation.invested_amount + total_need_amount
            setattr(donation, 'invested_amount', amount)
            await close_all_objects(CharityProject,session)
            print(f'Донат {donation.id}. Зачислено: {amount}')
            break        
        await session.commit()
        return None

    
async def distribute_amounts(pool_amount, primary_model, secondary_model, session):
    """
    Функция для распределения пулла средств между первичной моделью-получателем
    и вторичной моделью-донором
    """
    objects = await get_not_fully_invested_objects(
        primary_model, session
    )
    left = pool_amount
    for object in objects:
        left = left - object.full_amount - object.invested_amount
        print(f'left: {left}, available: {object.full_amount - object.invested_amount}')
        if left > 0:
            print(f'Из доната {object.id}. Зачислено: {object.full_amount}')
            await close_object(object, session)
            continue
        if not object.invested_amount:
            amount = object.full_amount - abs(left)
        else:
            amount = object.invested_amount + pool_amount
        setattr(object, 'invested_amount', amount)
        await close_all_objects(secondary_model, session)
        print(f'Донат {object.id}. Зачислено: {amount}')
        break    
    pass