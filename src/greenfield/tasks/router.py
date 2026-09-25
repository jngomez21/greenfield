"""Endpoints HTTP de tareas (design.md § API)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from greenfield.auth import get_current_user
from greenfield.db import get_session
from greenfield.tasks import service
from greenfield.tasks.schemas import TaskCreate, TaskRead

router = APIRouter(prefix="/tasks", tags=["tasks"])

CurrentUser = Annotated[str, Depends(get_current_user)]
# scope="function": el commit ocurre antes de responder, no después (FastAPI >= 0.121).
DbSession = Annotated[Session, Depends(get_session, scope="function")]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_task(
    data: TaskCreate, sub: CurrentUser, session: DbSession, request: Request, response: Response
) -> TaskRead:
    task = service.create(session, sub, data)
    response.headers["Location"] = f"{request.url.path}/{task.id}"
    return TaskRead.model_validate(task)
