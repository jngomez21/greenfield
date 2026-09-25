"""Configuración leída de variables de entorno (12-factor)."""

import os
from dataclasses import dataclass
from functools import lru_cache

_REQUIRED = ("DATABASE_URL", "AUTH_ISSUER", "AUTH_AUDIENCE", "AUTH_JWKS_URL")


@dataclass(frozen=True)
class Settings:
    database_url: str
    auth_issuer: str
    auth_audience: str
    auth_jwks_url: str
    log_level: str


def load_settings() -> Settings:
    missing = [name for name in _REQUIRED if not os.environ.get(name)]
    if missing:
        raise RuntimeError(f"Faltan variables de entorno: {', '.join(missing)}")
    return Settings(
        database_url=os.environ["DATABASE_URL"],
        auth_issuer=os.environ["AUTH_ISSUER"],
        auth_audience=os.environ["AUTH_AUDIENCE"],
        auth_jwks_url=os.environ["AUTH_JWKS_URL"],
        log_level=(os.environ.get("LOG_LEVEL") or "INFO").upper(),  # logging exige mayúsculas
    )


@lru_cache
def get_settings() -> Settings:
    return load_settings()
