from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import crud
from database import get_db
from models import UserModel
from security import credentials_error, decode_token

# Reads "Authorization: Bearer <token>" and powers the Authorize button
# in /docs. tokenUrl is where /docs sends the username + password.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserModel:
    payload = decode_token(token, expected_type="access")
    # CHECKLIST: the role is re-read from the database on every request,
    # never trusted from the token. Demote or deactivate a user and it
    # takes effect immediately, not when their token expires.
    user = crud.get_user_by_username(db, payload["sub"])
    if user is None:
        raise credentials_error()
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return user


def require_role(role: str):
    """Dependency factory: Depends(require_role("admin"))."""

    def checker(user: UserModel = Depends(get_current_user)) -> UserModel:
        if user.role != role:
            # 403, not 401: we know who you are, you just aren't allowed.
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return user

    return checker
