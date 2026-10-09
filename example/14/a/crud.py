from decimal import Decimal

from sqlalchemy.orm import Session

from models import ProductModel, UserModel
from security import hash_password, verify_password


def get_user_by_username(db: Session, username: str) -> UserModel | None:
    return db.query(UserModel).filter(UserModel.username == username).first()


def create_user(db: Session, username: str, password: str, role: str = "customer") -> UserModel:
    # Hash BEFORE it touches the database. The plain password is never
    # stored, logged, or returned.
    row = UserModel(username=username, hashed_password=hash_password(password), role=role)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def authenticate(db: Session, username: str, password: str) -> UserModel | None:
    user = get_user_by_username(db, username)
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user


def seed(db: Session) -> None:
    """Demo data so you can try the shop right away. Only runs on empty tables."""
    if db.query(UserModel).count() == 0:
        for username, role in (("admin", "admin"), ("alice", "customer"), ("bob", "customer")):
            db.add(UserModel(
                username=username,
                hashed_password=hash_password(f"{username}-password"),
                role=role,
            ))
    if db.query(ProductModel).count() == 0:
        db.add_all([
            ProductModel(name="Coffee mug", description="350 ml, dishwasher safe",
                         price=Decimal("8.50"), stock=20),
            ProductModel(name="Notebook", description="A5, dotted, 120 pages",
                         price=Decimal("4.25"), stock=50),
            ProductModel(name="Desk lamp", description="LED, warm white",
                         price=Decimal("24.00"), stock=5),
            ProductModel(name="Sticker pack", description="Last one in stock!",
                         price=Decimal("2.00"), stock=1),
        ])
    db.commit()
