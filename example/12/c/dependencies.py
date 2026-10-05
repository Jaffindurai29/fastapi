import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import crud
from database import get_db
from models import UserModel
from security import decode_token

# Reads "Authorization: Bearer <token>" and hands the <token> part to
# the route. No header at all -> 401 "Not authenticated" automatically.
# tokenUrl tells /docs where the "Authorize" button should log in.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def credentials_error(detail: str = "Could not validate credentials") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserModel:
    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:  # subclass, so it must come first
        raise credentials_error("Token has expired")
    except jwt.InvalidTokenError:  # bad signature, garbage, wrong algorithm...
        raise credentials_error()

    if payload.get("type") != "access":
        raise credentials_error()

    username = payload.get("sub")
    user = crud.get_user_by_username(db, username) if username else None
    if user is None:  # valid token, but the account was deleted since
        raise credentials_error()
    return user


# Builds on get_current_user: authenticated AND allowed in.
def get_current_active_user(user: UserModel = Depends(get_current_user)) -> UserModel:
    if not user.is_active:
        # 403, not 401: we know exactly who this is, and the answer is no.
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return user
