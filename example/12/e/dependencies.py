from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import crud
from database import get_db
from models import UserModel
from security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Authentication: WHO are you? Failing this is a 401.
def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = decode_access_token(token)
    if username is None:
        raise credentials_exception
    # A fresh row from the database on every request, so user.role is the
    # role RIGHT NOW, not the one written into the token at login time.
    user = crud.get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user


# Authorization: WHAT may you do? Failing this is a 403.
# require_role("admin") is not a dependency itself. It BUILDS one.
def require_role(*roles: str):
    def role_checker(user: UserModel = Depends(get_current_user)) -> UserModel:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return user

    return role_checker
