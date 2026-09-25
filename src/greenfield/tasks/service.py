"""Reglas de negocio de tareas. Toda consulta filtra por dueño (R1.3, R1.4, DEC-6)."""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from greenfield.errors import NotFoundError
from greenfield.tasks.models import Task
from greenfield.tasks.schemas import TaskCreate, TaskStatus


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


def get(session: Session, owner: str, task_id: uuid.UUID) -> Task:
    """Ajena o inexistente siguen el mismo camino: una sola query con el dueño (DEC-6)."""
    task = session.scalar(select(Task).where(Task.id == task_id, Task.owner_sub == owner))
    if task is None:
        raise NotFoundError
    return task


def update(session: Session, owner: str, task_id: uuid.UUID, changes: dict[str, Any]) -> Task:
    """Aplica sólo los campos enviados; el UPDATE lleva sólo lo que cambió (R4.1, R4.7)."""
    task = get(session, owner, task_id)
    modified = False
    for field, value in changes.items():
        if getattr(task, field) != value:
            setattr(task, field, value)
            modified = True
    if modified:  # R4.2: sin cambio real no se toca updated_at
        task.updated_at = datetime.now(UTC)
        session.flush()
    return task


def list_tasks(
    session: Session, owner: str, status: TaskStatus | None, limit: int, offset: int
) -> tuple[list[Task], int]:
    query = select(Task).where(Task.owner_sub == owner)
    if status is not None:
        query = query.where(Task.status == status.value)
    total = session.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = session.scalars(
        query.order_by(Task.created_at.desc(), Task.id.desc()).limit(limit).offset(offset)
    )
    return list(items), total
