from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import crud
from database import Base, SessionLocal, engine, get_db
from dependencies import get_current_user, get_note_for_user
from models import NoteModel, UserModel
from schemas import NoteIn, NoteOut, Token
from security import create_access_token

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed(db)

app = FastAPI()

NOTE_ERRORS = {
    403: {"description": "Not your note"},
    404: {"description": "Note not found"},
}


@app.post("/token", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form.username, form.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_access_token(user.username, user.role), "token_type": "bearer"}


@app.get("/notes", response_model=list[NoteOut])
def list_notes(user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role == "admin":
        return crud.get_all_notes(db)
    return crud.get_notes_for_owner(db, user.id)


# The owner is ALWAYS the logged-in user, never something from the body.
@app.post("/notes", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(
    note: NoteIn, user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)
):
    return crud.create_note(db, note, owner_id=user.id)


# get_note_for_user already did the 404 and 403 checks before we get here.
@app.get("/notes/{note_id}", response_model=NoteOut, responses=NOTE_ERRORS)
def read_note(note: NoteModel = Depends(get_note_for_user)):
    return note


@app.put("/notes/{note_id}", response_model=NoteOut, responses=NOTE_ERRORS)
def replace_note(
    body: NoteIn,
    note: NoteModel = Depends(get_note_for_user),
    db: Session = Depends(get_db),
):
    return crud.update_note(db, note, body)


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT, responses=NOTE_ERRORS)
def delete_note(note: NoteModel = Depends(get_note_for_user), db: Session = Depends(get_db)):
    crud.delete_note(db, note)
