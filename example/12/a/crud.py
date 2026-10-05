from sqlalchemy.orm import Session

from models import UserModel
from security import hash_password, verify_password


def get_users(db: Session) -> list[UserModel]:
    return db.query(UserModel).order_by(UserModel.id).all()


def get_user_by_username(db: Session, username: str) -> UserModel | None:
    return db.query(UserModel).filter(UserModel.username == username).first()


def create_user(db: Session, username: str, password: str) -> UserModel:
    # Hash BEFORE it touches the database. The plain password is
    # never stored, logged, or returned.
    row = UserModel(username=username, hashed_password=hash_password(password))
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def authenticate(db: Session, username: str, password: str) -> UserModel | None:
    user = get_user_by_username(db, username)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def seed_users(db: Session) -> None:
    if db.query(UserModel).count() == 0:
        for name in ("alice", "bob", "admin"):
            db.add(UserModel(username=name, hashed_password=hash_password(f"{name}-password")))
        db.commit()
