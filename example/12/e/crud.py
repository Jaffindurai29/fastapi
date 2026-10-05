from sqlalchemy.orm import Session

from models import UserModel
from security import hash_password, verify_password


def get_user(db: Session, user_id: int) -> UserModel | None:
    return db.get(UserModel, user_id)


def get_user_by_username(db: Session, username: str) -> UserModel | None:
    return db.query(UserModel).filter(UserModel.username == username).first()


def get_users(db: Session) -> list[UserModel]:
    return db.query(UserModel).order_by(UserModel.id).all()


def authenticate_user(db: Session, username: str, password: str) -> UserModel | None:
    user = get_user_by_username(db, username)
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user


def set_role(db: Session, user: UserModel, role: str) -> UserModel:
    user.role = role
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: UserModel) -> None:
    db.delete(user)
    db.commit()


def seed_users(db: Session) -> None:
    if db.query(UserModel).count() == 0:
        db.add_all(
            [
                UserModel(username="alice", hashed_password=hash_password("alice-password"), role="user"),
                UserModel(username="bob", hashed_password=hash_password("bob-password"), role="user"),
                UserModel(username="admin", hashed_password=hash_password("admin-password"), role="admin"),
            ]
        )
        db.commit()
