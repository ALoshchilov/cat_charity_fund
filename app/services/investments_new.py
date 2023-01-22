from typing import Union

from app.models import CharityProject, Donation


def distribute_amounts_new(
    source_objects: list[Union[CharityProject, Donation]],
    target_obj: Union[CharityProject, Donation],
):

    def update_object(
        obj: Union[CharityProject, Donation],
        amount: int
    ):
        obj.invested_amount = (obj.invested_amount or 0) + amount
        if obj.full_amount == obj.invested_amount:
            obj.close()

    updated_objects = []
    for source_obj in source_objects:
        amount = min(source_obj.get_remains(), target_obj.get_remains())
        update_object(target_obj, amount)
        update_object(source_obj, amount)
        updated_objects.append(source_obj)
        if target_obj.fully_invested:
            break
    return updated_objects
