from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Integer

from app.core.db import Base


class DonationProjectBaseModel(Base):

    __abstract__ = True

    __table_args__ = (
        CheckConstraint(
            'full_amount > 0',
            name='positive_full_amount_check',
        ),
        CheckConstraint(
            'full_amount >= invested_amount',
            name='full_ge_invested_amount_check',
        ),
    )

    full_amount = Column(Integer, nullable=False)
    invested_amount = Column(Integer, default=0)
    fully_invested = Column(Boolean, default=False)
    create_date = Column(DateTime, default=datetime.now)
    close_date = Column(DateTime)

    def get_remains(self) -> int:
        return self.full_amount - self.invested_amount

    def close(self):
        self.fully_invested = True
        self.invested_amount = self.full_amount
        self.close_date = datetime.now()
        return self

    def __repr__(self) -> str:
        return (
            f'Model: {self.__class__.__name__}; '
            f'Object_id: {self.id}; Full_amount: {self.full_amount}; '
            f'invested_amount: {self.invested_amount}; '
            f'Fully_invested: {self.fully_invested}; '
            f'Create_date: {self.create_date}; Close_date: {self.close_date};'
        )
