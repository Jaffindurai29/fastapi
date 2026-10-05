import logging

from cryptography.fernet import InvalidToken
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

import crud
from database import Base, SessionLocal, engine, get_db
from encryption import decrypt
from models import CustomerModel
from schemas import CustomerCreate, CustomerOut, CustomerRawOut

logger = logging.getLogger("uvicorn.error")

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed_customers(db)

app = FastAPI()

NOT_FOUND = {404: {"description": "Customer not found"}}


# Wrong FERNET_KEY (or a tampered value) -> InvalidToken. That's a server
# misconfiguration, not the client's fault, so: 500, a clear log line for
# the developer, and nothing secret in the response.
@app.exception_handler(InvalidToken)
def invalid_token_handler(request: Request, exc: InvalidToken):
    logger.error(
        "Could not decrypt a stored value on %s %s. Is FERNET_KEY the key the "
        "data was encrypted with?",
        request.method,
        request.url.path,
    )
    return JSONResponse(status_code=500, content={"detail": "Could not decrypt stored data"})


# Decrypt on the way OUT.
def to_out(row: CustomerModel) -> CustomerOut:
    return CustomerOut(
        id=row.id,
        name=row.name,
        email=row.email,
        phone=decrypt(row.phone_encrypted),
        notes=decrypt(row.notes_encrypted) if row.notes_encrypted is not None else None,
    )


def get_or_404(db: Session, customer_id: int) -> CustomerModel:
    row = crud.get_customer(db, customer_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return row


@app.get("/customers", response_model=list[CustomerOut])
def list_customers(db: Session = Depends(get_db)):
    return [to_out(row) for row in crud.get_customers(db)]


@app.get("/customers/{customer_id}", response_model=CustomerOut, responses=NOT_FOUND)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    return to_out(get_or_404(db, customer_id))


@app.post("/customers", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    return to_out(crud.create_customer(db, customer))


# LEARNING ONLY. Shows exactly what is stored in the database so you can
# see the ciphertext. A real app must NOT have a route like this.
@app.get("/customers/{customer_id}/raw", response_model=CustomerRawOut, responses=NOT_FOUND)
def get_customer_raw(customer_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, customer_id)
