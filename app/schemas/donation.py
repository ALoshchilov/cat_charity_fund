from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field, root_validator, validator
from pydantic.types import PositiveInt

from app.core.db import Base


class DonationBase(BaseModel):
    comment: Optional[str] = Field(None, min_length=1)
    full_amount: Optional[PositiveInt]


class DonationCreate(DonationBase):
    comment: str = Field(..., min_length=1)
    full_amount: Optional[PositiveInt]


class DonationUpdate(DonationBase):
    pass


class DonationDB(DonationBase):
    id: int
    user_id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime]

    class Config:
        orm_mode = True