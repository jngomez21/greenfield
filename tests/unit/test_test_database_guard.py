import pytest

from tests.conftest import ensure_test_database


def test_guard_acepta_base_terminada_en_test() -> None:
    url = "postgresql+psycopg://u:p@localhost:5433/greenfield_test"
    assert ensure_test_database(url) == url


@pytest.mark.parametrize(
    "url",
    [
        None,
        "",
        "postgresql+psycopg://u:p@localhost:5433/greenfield",
        "postgresql+psycopg://u:p@localhost:5433/greenfield_test_backup",
    ],
)
def test_guard_rechaza_url_ausente_o_base_sin_sufijo_test(url: str | None) -> None:
    with pytest.raises(ValueError):
        ensure_test_database(url)


def test_guard_no_revela_la_clave_en_el_mensaje() -> None:
    with pytest.raises(ValueError) as exc:
        ensure_test_database("postgresql+psycopg://u:SECRETO@localhost:5433/greenfield")
    assert "SECRETO" not in str(exc.value)
