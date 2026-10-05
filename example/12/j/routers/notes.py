from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud
from database import get_db
from dependencies import get_current_user
from models import NoteModel, UserModel
from schemas import NoteCreate, NoteOut

router = APIRouter(prefix="/notes", tags=["notes"])

NOTE_ERRORS = {403: {"description": "Not your note"}, 404: {"description": "Note not found"}}


def get_owned_note(db: Session, note_id: int, user: UserModel) -> NoteModel:
    """Load a note and check the current user may touch it."""
    note = crud.get_note(db, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    # Ownership check: logged in is not enough, it has to be YOUR note.
    # Admins may act on any note.
    if note.owner_id != user.id and user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't own this note")
    return note


@router.get("", response_model=list[NoteOut])
def list_notes(db: Session = Depends(get_db), user: UserModel = Depends(get_current_user)):
    # Users see their own notes; admins see everyone's.
    owner_id = None if user.role == "admin" else user.id
    return crud.get_notes(db, owner_id=owner_id)


@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(data: NoteCreate, db: Session = Depends(get_db), user: UserModel = Depends(get_current_user)):
    return crud.create_note(db, data, owner_id=user.id)


@router.get("/{note_id}", response_model=NoteOut, responses=NOTE_ERRORS)
def read_note(note_id: int, db: Session = Depends(get_db), user: UserModel = Depends(get_current_user)):
    return get_owned_note(db, note_id, user)


@router.put("/{note_id}", response_model=NoteOut, responses=NOTE_ERRORS)
def update_note(
    note_id: int, data: NoteCreate, db: Session = Depends(get_db), user: UserModel = Depends(get_current_user)
):
    return crud.update_note(db, get_owned_note(db, note_id, user), data)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT, responses=NOTE_ERRORS)
def delete_note(note_id: int, db: Session = Depends(get_db), user: UserModel = Depends(get_current_user)):
    crud.delete_note(db, get_owned_note(db, note_id, user))
