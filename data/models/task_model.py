from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import CheckConstraint, func
from data.db import Base
from datetime import datetime


class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True)

    priority: Mapped[int] = mapped_column(CheckConstraint("priority between 0 and 100"))

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    started_at: Mapped[datetime|None] = mapped_column()

    completed_at: Mapped[datetime|None] = mapped_column(CheckConstraint("completed_at > started_at and completed_at is not null and started_at is not null "))

    __table_args__ = (
        CheckConstraint("priority between 0 and 100", name = "check_priority_range"),
        CheckConstraint("completed_at > started_at and completed_at is not null and started_at is not null", name = "check_task_dates")
    )