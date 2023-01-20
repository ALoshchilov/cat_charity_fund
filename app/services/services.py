from datetime import datetime
from typing import Union

from fastapi import HTTPException
from sqlalchemy import asc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.core.messages import COMMON_ERROR
from app.models import CharityProject, Donation


async def get_not_fully_invested_objects(
    model: Union[CharityProject, Donation],
    session: AsyncSession
):
    db_objects = await session.execute(
        select(model).where(
            model.fully_invested.is_(False)
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
        model.fully_invested.is_(False)
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
    await session.execute(
        update(model).
        where(model.fully_invested.is_(False)).
        values(
            fully_invested=True,
            invested_amount=model.full_amount,
            close_date=datetime.now()
        )
    )


async def distribute_amounts(
    amount: int,
    covered_model: Union[CharityProject, Donation],
    not_covered_model: Union[CharityProject, Donation],
    session: AsyncSession
):
    """
    Функция для распределения средств между объектами модели covered_model,
    которые могут быть полностью закрыты из имеющихся средств, и объектами
    модели not_covered_model, средств для полного закрытия которых недостаточно
    """
    objects = await get_not_fully_invested_objects(
        not_covered_model, session
    )
    left = amount
    for object in objects:
        left = left - (object.full_amount - object.invested_amount)
        if left >= 0:
            await close_object(object, session)
            continue
        if not object.invested_amount:
            amount = object.full_amount - abs(left)
        else:
            amount = object.invested_amount + amount
        setattr(object, 'invested_amount', amount)
        await close_all_objects(covered_model, session)
        return


async def invest_all_donations(
    session: AsyncSession
):
    try:
        total_unused_amount = await get_total_not_invested(
            Donation, session
        ) or 0
        total_need_amount = await get_total_not_invested(
            CharityProject, session
        ) or 0
        if total_unused_amount == total_need_amount:
            await close_all_objects(CharityProject, session)
            await close_all_objects(Donation, session)
        elif total_unused_amount < total_need_amount:
            await distribute_amounts(
                amount=total_unused_amount,
                not_covered_model=CharityProject,
                covered_model=Donation,
                session=session
            )
        else:
            await distribute_amounts(
                amount=total_need_amount,
                not_covered_model=Donation,
                covered_model=CharityProject,
                session=session,
            )
        await session.commit()
    except Exception as error:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=COMMON_ERROR.format(error=str(error)),
        )
