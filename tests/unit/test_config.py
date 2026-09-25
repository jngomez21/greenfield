import pytest

from greenfield.config import load_settings

REQUIRED = ("DATABASE_URL", "AUTH_ISSUER", "AUTH_AUDIENCE", "AUTH_JWKS_URL")


@pytest.fixture
def full_env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    for name in REQUIRED:
        monkeypatch.setenv(name, f"valor-{name}")
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    return monkeypatch


def test_config_lee_variables_y_log_level_por_defecto(full_env: pytest.MonkeyPatch) -> None:
    settings = load_settings()
    assert settings.database_url == "valor-DATABASE_URL"
    assert settings.auth_jwks_url == "valor-AUTH_JWKS_URL"
    assert settings.log_level == "INFO"


def test_config_falla_listando_las_variables_que_faltan(full_env: pytest.MonkeyPatch) -> None:
    full_env.delenv("AUTH_ISSUER")
    full_env.setenv("AUTH_AUDIENCE", "")
    with pytest.raises(RuntimeError, match="AUTH_ISSUER, AUTH_AUDIENCE"):
        load_settings()
