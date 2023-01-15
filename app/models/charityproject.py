from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped

from app.core.db import Base
from app.models import DonationProjectBaseModel


class CharityProject(DonationProjectBaseModel):

    __tablename__ = 'charityproject'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    
    __mapper_args__ = {
        'concrete': True
    }

