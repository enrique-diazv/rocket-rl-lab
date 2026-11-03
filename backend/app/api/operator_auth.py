import os
from secrets import compare_digest
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


operator_bearer = HTTPBearer(
    auto_error=False,
    scheme_name="OperatorToken",
)


def require_operator(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(operator_bearer),
    ],
) -> None:
    expected_token = os.environ.get("ROCKET_OPERATOR_TOKEN", "").strip()

    if len(expected_token) < 32:
        raise HTTPException(
            status_code=503,
            detail="Las operaciones de escritura no están configuradas.",
        )

    if credentials is None or not compare_digest(
        credentials.credentials.encode("utf-8"),
        expected_token.encode("utf-8"),
    ):
        raise HTTPException(
            status_code=401,
            detail="Credenciales de operador inválidas.",
            headers={"WWW-Authenticate": "Bearer"},
        )