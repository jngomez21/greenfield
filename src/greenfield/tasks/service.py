"""Reglas de negocio de tareas. Toda consulta filtra por dueño (R1.3, R1.4, DEC-6)."""

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from greenfield.tasks.models import Task
from greenfield.tasks.schemas import TaskCreate


def create(session: Session, owner: str, data: TaskCreate) -> Task:
    now = datetime.now(UTC)
    task = Task(
        id=uuid.uuid4(),
        owner_sub=owner,
        title=data.title,
        description=data.description,
        status=data.status.value,
        due_date=data.due_date,
        created_at=now,
        updated_at=now,
    )
    session.add(task)
    session.flush()  # errores de BD antes de responder
    return task
