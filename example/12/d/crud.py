from sqlalchemy.orm import Session

from models import UserModel
from security import hash_password, verify_password


def get_user_by_username(db: Session, username: str) -> UserModel | None:
    return db.query(UserModel).filter(UserModel.username == username).first()


def authenticate(db: Session, username: str, password: str) -> UserModel | None:
    user = get_user_by_username(db, username)
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user


def seed_users(db: Session) -> None:
    if db.query(UserModel).count() == 0:
        db.add_all(
            [
                UserModel(username="alice", hashed_password=hash_password("alice-password")),
                UserModel(username="bob", hashed_password=hash_password("bob-password")),
                UserModel(username="admin", hashed_password=hash_password("admin-password")),
                # Deactivated account: can log in, but the protected
                # routes from 12/c on turn it away with 403.
                UserModel(username="carol", hashed_password=hash_password("carol-password"), is_active=False),
            ]
        )
        db.commit()
