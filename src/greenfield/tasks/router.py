"""Endpoints HTTP de tareas (design.md § API)."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from greenfield.auth import get_current_user
from greenfield.db import get_session
from greenfield.errors import NotFoundError
from greenfield.tasks import service
from greenfield.tasks.schemas import Page, TaskCreate, TaskRead, TaskStatus

router = APIRouter(prefix="/tasks", tags=["tasks"])

CurrentUser = Annotated[str, Depends(get_current_user)]
# scope="function": el commit ocurre antes de responder, no después (FastAPI >= 0.121).
DbSession = Annotated[Session, Depends(get_session, scope="function")]
Limit = Annotated[int, Query(ge=1, le=100)]
Offset = Annotated[int, Query(ge=0)]
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


@router.get("/{task_id}")
def get_task(task_id: str, sub: CurrentUser, session: DbSession) -> TaskRead:
    return TaskRead.model_validate(service.get(session, sub, _parse_id(task_id)))
