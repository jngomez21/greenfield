from datetime import UTC, date, datetime, timedelta

import pytest

from greenfield.tasks.router import get_today
from greenfield.tasks.service import is_overdue

TODAY = date(2026, 10, 10)


# Derived from R6.3
@pytest.mark.parametrize(
    ("due_date", "expected"),
    [
        (None, False),
        (TODAY - timedelta(days=1), True),
        (TODAY, False),  # vence hoy: todavía no está vencida
        (TODAY + timedelta(days=1), False),
    ],
)
def test_vencida_solo_si_la_fecha_limite_es_anterior_a_hoy(
    due_date: date | None, expected: bool
) -> None:
    assert is_overdue(due_date, TODAY) is expected


# Derived from R6.3
def test_hoy_se_calcula_en_utc() -> None:
    assert get_today() == datetime.now(UTC).date()
