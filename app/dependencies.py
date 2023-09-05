from typing import Annotated

from fastapi import Cookie, HTTPException
from jose import JWTError, jwt as josejwt

from app.config import get_settings

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
