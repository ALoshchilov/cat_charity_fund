from sqlalchemy import Column, ForeignKey, Integer, Text

from app.models import DonationProjectBaseModel


class Donation(DonationProjectBaseModel):

    __tablename__ = 'donation'

    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text, nullable=True)

    __mapper_args__ = {
        'concrete': True
    }

    def __repr__(self) -> str:
        return (
            f'{super(self.__class__, self).__repr__()}'
            f' UserID: {self.user_id}; Comment: {self.comment}.'
        )
