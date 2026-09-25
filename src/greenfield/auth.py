"""Autenticación: Bearer JWT de un IdP OIDC externo (design.md DEC-10, stack/security.md)."""

from collections.abc import Callable
from functools import lru_cache
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from greenfield.config import get_settings

ALGORITHMS = ["RS256", "ES256"]  # lista cerrada: fuera `none` y HS*
LEEWAY_SECONDS = 30
REQUIRED_CLAIMS = ["exp", "iss", "aud", "sub"]

KeyResolver = Callable[[str], Any]

_bearer = HTTPBearer(auto_error=False)


@lru_cache
def _jwks_client() -> jwt.PyJWKClient:
    return jwt.PyJWKClient(get_settings().auth_jwks_url)  # cachea las llaves del IdP


def get_key_resolver() -> KeyResolver:
    """Fuente de la llave de firma; los tests la sustituyen por una llave local (D1 en MOCK)."""
    client = _jwks_client()
    return lambda token: client.get_signing_key_from_jwt(token).key


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales ausentes o inválidas.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    resolve_key: Annotated[KeyResolver, Depends(get_key_resolver)],
) -> str:
    """Devuelve el `sub` del token o responde 401 (R1.1)."""
    if credentials is None:
        raise _unauthorized()
    settings = get_settings()
    token = credentials.credentials
    try:
        claims = jwt.decode(
            token,
            resolve_key(token),
            algorithms=ALGORITHMS,
            audience=settings.auth_audience,
            issuer=settings.auth_issuer,
            leeway=LEEWAY_SECONDS,
            options={"require": REQUIRED_CLAIMS},
        )
    except jwt.PyJWKClientConnectionError:
        raise  # IdP inaccesible: es una falla del servidor, no del cliente
    except jwt.PyJWTError:
        raise _unauthorized() from None
    request.state.sub = sub = str(claims["sub"])  # para el access log
    return sub
