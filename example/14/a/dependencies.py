from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

import crud
from database import get_db
from models import UserModel
from security import decode_token

# Reads "Authorization: Bearer <token>". auto_error=False so a missing
# header gets OUR 401 below, not FastAPI's default 403.
bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> UserModel:
    """401 = "who are you?" No token, or a bad/expired one."""
    username = decode_token(creds.credentials, expected_type="access") if creds else None
    user = crud.get_user_by_username(db, username) if username else None
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token invalid or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_roles(*roles: str):
    """403 = "I know who you are, and you're not allowed."

    Usage:  user = Depends(require_roles("admin"))
    """

    def checker(user: UserModel = Depends(get_current_user)) -> UserModel:
        # user.role comes from the DATABASE, not from the token, so a
        # demoted admin loses access on their very next request.
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
        return user

    return checker
