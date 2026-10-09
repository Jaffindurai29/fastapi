from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, require_roles
from ids import decode_id
from models import OrderItemModel, OrderModel, ProductModel, UserModel
from schemas import OrderCreate, OrderOut, StatusUpdate
from encryption import encrypt

router = APIRouter(prefix="/orders", tags=["orders"])

# Which status may follow which. Anything else is refused.
NEXT_STATUS = {
    "pending": {"shipped", "cancelled"},
    "shipped": {"delivered"},
    "delivered": set(),
    "cancelled": set(),
}


def get_order_or_404(db: Session, order_id: str, user: UserModel) -> OrderModel:
    order = db.get(OrderModel, decode_id(order_id))
    # Someone else's order gets 404, not 403: we don't even admit it exists.
    # THIS check is what protects orders; the hashed id only hides the count.
    if order is None or (order.user_id != user.id and user.role != "admin"):
        raise HTTPException(status_code=404, detail="Order not found")
    return order


def lock_products(db: Session, product_ids) -> dict[int, ProductModel]:
    # SELECT ... FOR UPDATE: other requests touching these rows wait until
    # we commit. Two people buying the last item can't both succeed.
    # Sorted by id so two orders always lock in the same order (no deadlock).
    rows = (
        db.query(ProductModel)
        .filter(ProductModel.id.in_(product_ids))
        .order_by(ProductModel.id)
        .with_for_update()
        .all()
    )
    return {p.id: p for p in rows}


def restore_stock(db: Session, order: OrderModel) -> None:
    products = lock_products(db, [item.product_id for item in order.items])
    for item in order.items:
        products[item.product_id].stock += item.quantity


# ------------------------------------------------------------ customer ----

@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED,
             responses={404: {"description": "Product not found"},
                        409: {"description": "Not enough stock"}})
def place_order(body: OrderCreate, db: Session = Depends(get_db),
                user: UserModel = Depends(require_roles("customer"))):
    # Same product listed twice? Add the quantities together.
    wanted: dict[int, int] = {}
    for item in body.items:
        pid = decode_id(item.product_id)
        wanted[pid] = wanted.get(pid, 0) + item.quantity

    products = lock_products(db, wanted)

    # Check EVERYTHING before changing anything: all items or none.
    for pid, qty in wanted.items():
        product = products.get(pid)
        if product is None or not product.is_active:
            raise HTTPException(status_code=404, detail="Product not found")
        if product.stock < qty:
            raise HTTPException(
                status_code=409,
                detail=f"Only {product.stock} of {product.name} left",
            )

    order = OrderModel(
        user_id=user.id,
        status="pending",
        total=Decimal("0"),
        phone_encrypted=encrypt(body.phone),
        address_encrypted=encrypt(body.address),
    )
    for pid, qty in wanted.items():
        product = products[pid]
        product.stock -= qty
        order.items.append(OrderItemModel(product_id=pid, quantity=qty, unit_price=product.price))
        order.total += product.price * qty

    db.add(order)
    db.commit()  # stock change and order are saved together, or not at all
    db.refresh(order)
    return order


@router.get("/mine", response_model=list[OrderOut])
def my_orders(db: Session = Depends(get_db), user: UserModel = Depends(get_current_user)):
    return (
        db.query(OrderModel)
        .filter(OrderModel.user_id == user.id)
        .order_by(OrderModel.id.desc())
        .all()
    )


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: str, db: Session = Depends(get_db),
              user: UserModel = Depends(get_current_user)):
    return get_order_or_404(db, order_id, user)


@router.post("/{order_id}/cancel", response_model=OrderOut,
             responses={400: {"description": "Only pending orders can be cancelled"}})
def cancel_order(order_id: str, db: Session = Depends(get_db),
                 user: UserModel = Depends(get_current_user)):
    order = get_order_or_404(db, order_id, user)
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="Only pending orders can be cancelled")
    order.status = "cancelled"
    restore_stock(db, order)
    db.commit()
    db.refresh(order)
    return order


# ---------------------------------------------------------- admin only ----

@router.get("", response_model=list[OrderOut])
def all_orders(db: Session = Depends(get_db), user: UserModel = Depends(require_roles("admin"))):
    return db.query(OrderModel).order_by(OrderModel.id.desc()).all()


@router.patch("/{order_id}/status", response_model=OrderOut,
              responses={400: {"description": "Status change not allowed"}})
def update_status(order_id: str, body: StatusUpdate, db: Session = Depends(get_db),
                  user: UserModel = Depends(require_roles("admin"))):
    order = get_order_or_404(db, order_id, user)
    if body.status not in NEXT_STATUS[order.status]:
        raise HTTPException(
            status_code=400,
            detail=f"Can't go from {order.status} to {body.status}",
        )
    if body.status == "cancelled":
        restore_stock(db, order)
    order.status = body.status
    db.commit()
    db.refresh(order)
    return order
