from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import crud
from database import get_db
from models import NoteModel, UserModel
from security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Same as 12/c and 12/e: who are you? (401)
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
    user = crud.get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user


# Ownership: may THIS user touch THIS note? (404 / 403)
# note_id comes from the path (/notes/{note_id}), so any route with that
# path parameter can just declare: note = Depends(get_note_for_user).
def get_note_for_user(
    note_id: int,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NoteModel:
    note = crud.get_note(db, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.owner_id != user.id and user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return note
