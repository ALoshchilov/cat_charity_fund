from typing import Union

from app.models import CharityProject, Donation


def distribute_amounts(
    sources: list[Union[CharityProject, Donation]],
    target: Union[CharityProject, Donation],
):
    updated_objects = []
    for source in sources:
        amount = min(source.get_remains(), target.get_remains())
        target.invest(amount)
        source.invest(amount)
        updated_objects.append(source)
        if target.fully_invested:
            break
    return updated_objects
