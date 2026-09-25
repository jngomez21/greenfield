"""Reglas de negocio de tareas. Toda consulta filtra por dueño (R1.3, R1.4, DEC-6)."""

import uuid
from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy import Select, func, select
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


def delete(session: Session, owner: str, task_id: uuid.UUID) -> None:
    """Borrado físico (R5.1)."""
    session.delete(get(session, owner, task_id))
    session.flush()


def _page(
    session: Session, query: Select[Task], order: tuple[Any, ...], limit: int, offset: int
) -> tuple[list[Task], int]:
    """Página + total con el mismo filtro (R3.7, R6.6, DEC-8)."""
    total = session.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = session.scalars(query.order_by(*order).limit(limit).offset(offset))
    return list(items), total


def list_tasks(
    session: Session, owner: str, status: TaskStatus | None, limit: int, offset: int
) -> tuple[list[Task], int]:
    query = select(Task).where(Task.owner_sub == owner)
    if status is not None:
        query = query.where(Task.status == status.value)
    return _page(session, query, (Task.created_at.desc(), Task.id.desc()), limit, offset)


def is_overdue(due_date: date | None, today: date) -> bool:
    """Vencida = fecha límite anterior a hoy (UTC); la que vence hoy no lo está (R6.3)."""
    return due_date is not None and due_date < today


def list_pending(
    session: Session, owner: str, today: date, overdue_only: bool, limit: int, offset: int
) -> tuple[list[Task], int]:
    # `<> 'completed'` (no IN pending/in_progress): así usa el índice parcial de pendientes.
    query = select(Task).where(Task.owner_sub == owner, Task.status != TaskStatus.completed.value)
    if overdue_only:
        query = query.where(Task.due_date < today)
    order = (Task.due_date.asc().nulls_last(), Task.created_at.asc(), Task.id.asc())
    return _page(session, query, order, limit, offset)
