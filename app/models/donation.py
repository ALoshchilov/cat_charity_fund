from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text

from app.core.db import Base
from app.models import DonationProjectBaseModel

class Donation(DonationProjectBaseModel):

    __tablename__ = 'donation'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text, nullable=True)

    __mapper_args__ = {
        'concrete': True
    }
