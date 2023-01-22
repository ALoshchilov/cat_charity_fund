from sqlalchemy import Column, String, Text

from app.models import DonationProjectBaseModel


class CharityProject(DonationProjectBaseModel):

    __tablename__ = 'charityproject'

    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)

    __mapper_args__ = {
        'concrete': True
    }

    def __repr__(self) -> str:
        return (
            f'{super().__repr__()}'
            f' Name: {self.name[:15]}; Description: {self.description}.'
        )
