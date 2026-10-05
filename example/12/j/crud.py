from sqlalchemy.orm import Session

from models import NoteModel, RefreshTokenModel, UserModel
from schemas import NoteCreate, UserCreate
from security import hash_password


# ---- users ----

def get_user_by_username(db: Session, username: str) -> UserModel | None:
    return db.query(UserModel).filter(UserModel.username == username).first()


def get_users(db: Session) -> list[UserModel]:
    return db.query(UserModel).order_by(UserModel.id).all()


def create_user(db: Session, data: UserCreate, role: str = "user") -> UserModel:
    row = UserModel(username=data.username, hashed_password=hash_password(data.password), role=role)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


# ---- refresh tokens ----

def save_refresh_token(db: Session, jti: str, user_id: int) -> None:
    db.add(RefreshTokenModel(jti=jti, user_id=user_id))
    db.commit()


def get_refresh_token(db: Session, jti: str) -> RefreshTokenModel | None:
    return db.get(RefreshTokenModel, jti)


def revoke_refresh_token(db: Session, row: RefreshTokenModel) -> None:
    row.revoked = True
    db.commit()


# ---- notes ----

def get_notes(db: Session, owner_id: int | None = None) -> list[NoteModel]:
    query = db.query(NoteModel)
    if owner_id is not None:
        query = query.filter(NoteModel.owner_id == owner_id)
    return query.order_by(NoteModel.id).all()


def get_note(db: Session, note_id: int) -> NoteModel | None:
    return db.get(NoteModel, note_id)


def create_note(db: Session, data: NoteCreate, owner_id: int) -> NoteModel:
    # owner_id comes from the logged-in user, never from the request body.
    row = NoteModel(**data.model_dump(), owner_id=owner_id)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_note(db: Session, row: NoteModel, data: NoteCreate) -> NoteModel:
    row.title = data.title
    row.body = data.body
    db.commit()
    db.refresh(row)
    return row


def delete_note(db: Session, row: NoteModel) -> None:
    db.delete(row)
    db.commit()


# ---- demo data ----

def seed(db: Session) -> None:
    if db.query(UserModel).count() > 0:
        return
    alice = UserModel(username="alice", hashed_password=hash_password("alice-password"), role="user")
    bob = UserModel(username="bob", hashed_password=hash_password("bob-password"), role="user")
    admin = UserModel(username="admin", hashed_password=hash_password("admin-password"), role="admin")
    db.add_all([alice, bob, admin])
    db.flush()  # assigns the ids so the notes below can point at them
    db.add_all(
        [
            NoteModel(title="Alice's shopping list", body="Milk, eggs", owner_id=alice.id),
            NoteModel(title="Alice's secret", body="Only Alice (and admins) can read this", owner_id=alice.id),
            NoteModel(title="Bob's todo", body="Fix the bike", owner_id=bob.id),
        ]
    )
    db.commit()
