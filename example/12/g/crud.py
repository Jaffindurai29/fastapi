from sqlalchemy.orm import Session

from encryption import encrypt
from models import CustomerModel
from schemas import CustomerCreate


def get_customers(db: Session) -> list[CustomerModel]:
    return db.query(CustomerModel).order_by(CustomerModel.id).all()


def get_customer(db: Session, customer_id: int) -> CustomerModel | None:
    return db.get(CustomerModel, customer_id)


# Encrypt on the way IN. Plaintext phone/notes never reach the database.
def create_customer(db: Session, customer: CustomerCreate) -> CustomerModel:
    row = CustomerModel(
        name=customer.name,
        email=customer.email,
        phone_encrypted=encrypt(customer.phone),
        notes_encrypted=encrypt(customer.notes) if customer.notes is not None else None,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def seed_customers(db: Session) -> None:
    if db.query(CustomerModel).count() == 0:
        create_customer(
            db,
            CustomerCreate(
                name="Ada Lovelace",
                email="ada@example.com",
                phone="+44 20 7946 0018",
                notes="Prefers email. VIP.",
            ),
        )
        create_customer(
            db,
            CustomerCreate(name="Alan Turing", email="alan@example.com", phone="+44 161 496 0000"),
        )
