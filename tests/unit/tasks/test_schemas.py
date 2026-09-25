from datetime import date

import pytest
from pydantic import ValidationError

from greenfield.tasks.schemas import TaskCreate, TaskStatus, TaskUpdate


# Derived from R2.2
def test_estado_por_defecto_es_pending() -> None:
    assert TaskCreate(title="x").status is TaskStatus.pending


# Derived from R2.4
@pytest.mark.parametrize("title", ["", " ", " \t"])
def test_titulo_en_blanco_es_invalido(title: str) -> None:
    with pytest.raises(ValidationError):
        TaskCreate(title=title)


def test_titulo_se_guarda_tal_cual_se_envia() -> None:
    assert TaskCreate(title="  con espacios  ").title == "  con espacios  "


# Derived from R2.7
def test_fecha_limite_solo_acepta_aaaa_mm_dd() -> None:
    assert TaskCreate.model_validate({"title": "x", "due_date": "2026-10-01"}).due_date == date(
        2026, 10, 1
    )
    for invalid in ["2026-10-01T00:00:00", "2026-02-30", 1700000000]:
        with pytest.raises(ValidationError):
            TaskCreate.model_validate({"title": "x", "due_date": invalid})


# Derived from R4.1
def test_update_distingue_ausente_de_nulo() -> None:
    update = TaskUpdate.model_validate({"description": None})
    assert update.model_fields_set == {"description"}
    assert TaskUpdate.model_validate({}).model_fields_set == set()


# Derived from R4.5
@pytest.mark.parametrize("field", ["title", "status"])
def test_update_rechaza_nulo_en_campos_obligatorios(field: str) -> None:
    with pytest.raises(ValidationError):
        TaskUpdate.model_validate({field: None})
