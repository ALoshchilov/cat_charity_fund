from typing import Union

from app.models import CharityProject, Donation


def get_changed_objects(
    objects: list[Union[CharityProject, Donation]],
    amount: int
):
    changed_objects = []
    left = amount
    for obj in objects:
        left = left - obj.get_remains()
        if left > 0:
            changed_objects.append(obj.close())
            continue
        if not obj.invested_amount:
            obj.invested_amount = obj.full_amount - abs(left)
        elif obj.full_amount == obj.invested_amount + amount:
            changed_objects.append(obj.close())
        else:
            obj.invested_amount = obj.invested_amount + amount
        return changed_objects


def distribute_amounts(
    donations: list[Donation],
    projects: list[CharityProject]
) -> tuple[list[Donation], list[CharityProject]]:
    available_amount = sum([donation.get_remains() for donation in donations])
    needed_amount = sum([project.get_remains() for project in projects])
    if available_amount == needed_amount:
        return (
            [donation.close() for donation in donations],
            [project.close() for project in projects]
        )
    elif available_amount < needed_amount:
        return (
            [donation.close() for donation in donations],
            get_changed_objects(
                amount=available_amount,
                objects=projects
            )
        )
    else:
        return (
            get_changed_objects(
                amount=needed_amount,
                objects=donations
            ),
            [project.close() for project in projects]
        )