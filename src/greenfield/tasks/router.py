"""Endpoints HTTP de tareas (design.md § API)."""

import uuid
from datetime import UTC, date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from greenfield.auth import get_current_user
from greenfield.db import get_session
from greenfield.errors import NotFoundError
from greenfield.tasks import service
from greenfield.tasks.schemas import (
    Page,
    PendingTaskRead,
    TaskCreate,
    TaskRead,
    TaskStatus,
    TaskUpdate,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])

CurrentUser = Annotated[str, Depends(get_current_user)]
# scope="function": el commit ocurre antes de responder, no después (FastAPI >= 0.121).
DbSession = Annotated[Session, Depends(get_session, scope="function")]
Limit = Annotated[int, Query(ge=1, le=100)]
Offset = Annotated[int, Query(ge=0, le=2**63 - 1)]  # tope de bigint: más allá, la BD da 500
StatusFilter = Annotated[TaskStatus | None, Query(alias="status")]


def _parse_id(task_id: str) -> uuid.UUID:
    """ID con formato inválido = tarea inexistente: 404, no 422 (R3.2, DEC-4)."""
    try:
        return uuid.UUID(task_id)
    except ValueError:
        raise NotFoundError from None


@router.post("", status_code=status.HTTP_201_CREATED)
def create_task(
    data: TaskCreate, sub: CurrentUser, session: DbSession, request: Request, response: Response
) -> TaskRead:
    task = service.create(session, sub, data)
    response.headers["Location"] = f"{request.url.path}/{task.id}"
    return TaskRead.model_validate(task)


@router.get("")
def list_tasks(
    sub: CurrentUser,
    session: DbSession,
    status_filter: StatusFilter = None,
    limit: Limit = 50,
    offset: Offset = 0,
) -> Page[TaskRead]:
    items, total = service.list_tasks(session, sub, status_filter, limit, offset)
    return Page[TaskRead](
        items=[TaskRead.model_validate(t) for t in items], total=total, limit=limit, offset=offset
    )


def get_today() -> date:
    """Fecha de hoy en UTC, igual para todos los usuarios (R6.3, DEC-5); los tests la fijan."""
    return datetime.now(UTC).date()


Today = Annotated[date, Depends(get_today)]


# Registrada antes de /{task_id} para que la ruta fija gane (DEC-4).
@router.get("/pending")
def list_pending_tasks(
    sub: CurrentUser,
    session: DbSession,
    today: Today,
    overdue: bool = False,
    limit: Limit = 50,
    offset: Offset = 0,
) -> Page[PendingTaskRead]:
    items, total = service.list_pending(session, sub, today, overdue, limit, offset)
    return Page[PendingTaskRead](
        items=[
            PendingTaskRead(
                **TaskRead.model_validate(t).model_dump(),
                is_overdue=service.is_overdue(t.due_date, today),
            )
            for t in items
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{task_id}")
def get_task(task_id: str, sub: CurrentUser, session: DbSession) -> TaskRead:
    return TaskRead.model_validate(service.get(session, sub, _parse_id(task_id)))


@router.patch("/{task_id}")
def update_task(task_id: str, data: TaskUpdate, sub: CurrentUser, session: DbSession) -> TaskRead:
    # Sólo los campos presentes en el body (ausente = no cambia; DEC-3).
    changes = {field: getattr(data, field) for field in data.model_fields_set}
    if "status" in changes:
        changes["status"] = changes["status"].value
    return TaskRead.model_validate(service.update(session, sub, _parse_id(task_id), changes))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, sub: CurrentUser, session: DbSession) -> None:
    service.delete(session, sub, _parse_id(task_id))
