from sqlalchemy.orm import Session

from models import NoteModel, UserModel
from schemas import NoteIn
from security import hash_password, verify_password


# ---- users (same as 12/e) ----

def get_user_by_username(db: Session, username: str) -> UserModel | None:
    return db.query(UserModel).filter(UserModel.username == username).first()


def authenticate_user(db: Session, username: str, password: str) -> UserModel | None:
    user = get_user_by_username(db, username)
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user


# ---- notes ----

def get_note(db: Session, note_id: int) -> NoteModel | None:
    return db.get(NoteModel, note_id)


# The owner filter lives in the QUERY. Forget it and every user can
# read every note: that's the bug this lesson is about.
def get_notes_for_owner(db: Session, owner_id: int) -> list[NoteModel]:
    return (
        db.query(NoteModel)
        .filter(NoteModel.owner_id == owner_id)
        .order_by(NoteModel.id)
        .all()
    )


def get_all_notes(db: Session) -> list[NoteModel]:
    return db.query(NoteModel).order_by(NoteModel.id).all()


def create_note(db: Session, note: NoteIn, owner_id: int) -> NoteModel:
    row = NoteModel(**note.model_dump(), owner_id=owner_id)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_note(db: Session, row: NoteModel, note: NoteIn) -> NoteModel:
    row.title = note.title
    row.body = note.body
    db.commit()
    db.refresh(row)
    return row


def delete_note(db: Session, row: NoteModel) -> None:
    db.delete(row)
    db.commit()


# ---- seed ----

def seed(db: Session) -> None:
    # 12/e may already have created the users (same table).
    if db.query(UserModel).count() == 0:
        db.add_all(
            [
                UserModel(username="alice", hashed_password=hash_password("alice-password"), role="user"),
                UserModel(username="bob", hashed_password=hash_password("bob-password"), role="user"),
                UserModel(username="admin", hashed_password=hash_password("admin-password"), role="admin"),
            ]
        )
        db.commit()

    if db.query(NoteModel).count() == 0:
        notes = {
            "alice": [("Alice's shopping list", "milk, eggs"), ("Alice's diary", "Dear diary...")],
            "bob": [("Bob's passwords", "please don't read this")],
        }
        for username, items in notes.items():
            user = get_user_by_username(db, username)
            if user is None:  # deleted in 12/e? just skip
                continue
            for title, body in items:
                db.add(NoteModel(title=title, body=body, owner_id=user.id))
        db.commit()
