from typing import Annotated

from fastapi import Cookie, Depends, HTTPException
from jose import JWTError, jwt as josejwt
from psycopg import Connection

from app.config import get_settings
from app.db import get_conn

settings = get_settings()


def get_current_user_id(jwt: Annotated[str | None, Cookie()] = None):
    if not jwt:
        raise HTTPException(status_code=401, detail="jwt token missing")
    try:
        payload = josejwt.decode(jwt, settings.jwt_secret, algorithms=["HS256"])
        return payload.get("sub")
    except JWTError as e:
        print(e)
        raise HTTPException(status_code=401, detail="invalid credentials")


def get_db():
    with get_conn() as conn:
        yield conn


DBDep = Annotated[Connection, Depends(get_db)]
AuthDep = Annotated[str, Depends(get_current_user_id)]
