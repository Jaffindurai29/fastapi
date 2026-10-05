from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud
from database import get_db
from schemas import OrderCreate, OrderOut

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=list[OrderOut])
def list_orders(db: Session = Depends(get_db)):
    return crud.get_orders(db)


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    row = crud.get_order(db, order_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return row


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    try:
        return crud.place_order(db, data)
    except crud.OrderError as exc:
        # crud already rolled back; just turn it into an HTTP answer.
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


# Same input, same checks, but commits after every line. Here only to
# show what goes wrong. Never write it like this.
@router.post("/unsafe", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order_unsafe(data: OrderCreate, db: Session = Depends(get_db)):
    try:
        return crud.place_order_unsafe(db, data)
    except crud.OrderError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
