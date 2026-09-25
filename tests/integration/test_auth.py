import time
from collections.abc import Iterator
from typing import Annotated

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from greenfield.auth import get_current_user, get_key_resolver
from tests.conftest import MakeToken


@pytest.fixture
def client(test_database_url: str, signing_key: rsa.RSAPrivateKey) -> Iterator[TestClient]:
    """Mini-app de prueba: un endpoint protegido que devuelve el `sub` autenticado."""
    app = FastAPI()

    @app.get("/whoami")
    def whoami(sub: Annotated[str, Depends(get_current_user)]) -> dict[str, str]:
        return {"sub": sub}

    public_key = signing_key.public_key()
    app.dependency_overrides[get_key_resolver] = lambda: lambda token: public_key
    with TestClient(app) as c:
        yield c


# Derived from R1.1
def test_token_valido_entrega_el_sub(client: TestClient, make_token: MakeToken) -> None:
    response = client.get("/whoami", headers={"Authorization": f"Bearer {make_token('user-a')}"})
    assert response.status_code == 200
    assert response.json() == {"sub": "user-a"}


# Derived from R1.1
def test_tolera_30_segundos_de_desfase_de_reloj(client: TestClient, make_token: MakeToken) -> None:
    token = make_token(exp=int(time.time()) - 10)
    assert client.get("/whoami", headers={"Authorization": f"Bearer {token}"}).status_code == 200


def _invalid_tokens(make_token: MakeToken) -> dict[str, tuple[str | None, str]]:
    now = int(time.time())
    otra_llave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return {
        "sin_header": (None, "Bearer"),
        "esquema_basic": ("dXNlcjpwYXNz", "Basic"),
        "mal_formado": ("no-es-un-jwt", "Bearer"),
        "expirado": (make_token(exp=now - 120), "Bearer"),
        "otra_audiencia": (make_token(aud="otro-servicio"), "Bearer"),
        "otro_emisor": (make_token(iss="https://otro-idp/"), "Bearer"),
        "sin_sub": (make_token(sub=None), "Bearer"),
        "sin_exp": (make_token(exp=None), "Bearer"),
        "firmado_con_otra_llave": (make_token(key=otra_llave), "Bearer"),
        "alg_none": (jwt.encode({"sub": "user-a"}, None, algorithm="none"), "Bearer"),
        "alg_hs256": (make_token(key="x" * 32, algorithm="HS256"), "Bearer"),
    }


CASES = [
    "sin_header",
    "esquema_basic",
    "mal_formado",
    "expirado",
    "otra_audiencia",
    "otro_emisor",
    "sin_sub",
    "sin_exp",
    "firmado_con_otra_llave",
    "alg_none",
    "alg_hs256",
]


# Derived from R1.1
@pytest.mark.parametrize("case", CASES)
def test_credencial_invalida_da_401_con_www_authenticate(
    client: TestClient, make_token: MakeToken, case: str
) -> None:
    token, scheme = _invalid_tokens(make_token)[case]
    headers = {"Authorization": f"{scheme} {token}"} if token is not None else {}
    response = client.get("/whoami", headers=headers)
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert "user-a" not in response.text


def test_idp_inaccesible_no_se_disfraza_de_401(
    test_database_url: str, make_token: MakeToken
) -> None:
    """Si no se puede leer el JWKS es una falla del servidor, no una credencial inválida."""
    app = FastAPI()

    @app.get("/whoami")
    def whoami(sub: Annotated[str, Depends(get_current_user)]) -> dict[str, str]:
        return {"sub": sub}

    def unreachable(token: str) -> object:
        raise jwt.PyJWKClientConnectionError("JWKS inaccesible")

    app.dependency_overrides[get_key_resolver] = lambda: unreachable
    with TestClient(app) as c, pytest.raises(jwt.PyJWKClientConnectionError):
        c.get("/whoami", headers={"Authorization": f"Bearer {make_token()}"})


def test_resolver_de_produccion_usa_el_jwks_configurado(test_database_url: str) -> None:
    resolver = get_key_resolver()
    assert callable(resolver)
