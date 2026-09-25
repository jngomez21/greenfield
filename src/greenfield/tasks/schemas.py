"""Schemas de la API de tareas (design.md § Contratos). Campos en inglés (DEC-1)."""

import re
import uuid
from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Annotated, Any

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
)

_ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


class TaskStatus(StrEnum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


def _not_blank(value: str) -> str:
    if not value.strip():
        raise ValueError("El título no puede estar vacío ni contener sólo espacios.")
    return value  # se guarda tal cual se envía


def _iso_date(value: Any) -> Any:
    if not isinstance(value, str) or not _ISO_DATE.fullmatch(value):
        raise ValueError("La fecha límite debe tener el formato AAAA-MM-DD.")
    return value  # Pydantic valida después que sea una fecha de calendario real


Title = Annotated[str, Field(min_length=1, max_length=200), AfterValidator(_not_blank)]
Description = Annotated[str, Field(max_length=2000)]
DueDate = Annotated[date, BeforeValidator(_iso_date)]


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Title
    description: Description | None = None
    status: TaskStatus = TaskStatus.pending
    due_date: DueDate | None = None


class TaskUpdate(BaseModel):
    """Actualización parcial: ausente = no cambia; null quita description/due_date (DEC-3)."""

    model_config = ConfigDict(extra="forbid")

    title: Title | None = None
    description: Description | None = None
    status: TaskStatus | None = None
    due_date: DueDate | None = None

    @field_validator("title", "status", mode="before")
    @classmethod
    def _required_if_present(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("Este campo no se puede quitar.")
        return value


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None
    status: TaskStatus
    due_date: date | None
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def _utc(self, value: datetime) -> datetime:
        # La BD devuelve la zona de su sesión (p. ej. -05:00); la API siempre responde en UTC.
        return value.astimezone(UTC)


class Page[T](BaseModel):
    items: list[T]
    total: int
    limit: int
    offset: int
