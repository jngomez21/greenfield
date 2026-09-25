import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, DateTime, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from greenfield.db import Base


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint("btrim(title) <> ''", name="ck_tasks_title_not_blank"),
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed')", name="ck_tasks_status"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    owner_sub: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(String(2000))
    status: Mapped[str] = mapped_column(Text, server_default="pending")
    due_date: Mapped[date | None]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


Index("ix_tasks_owner_created", Task.owner_sub, Task.created_at.desc(), Task.id.desc())
Index(
    "ix_tasks_owner_pending",
    Task.owner_sub,
    Task.due_date,
    Task.created_at,
    Task.id,
    postgresql_where=text("status <> 'completed'"),
)
