from sqlalchemy.orm import Session, selectinload

from models import OrderLineModel, OrderModel, ProductModel
from schemas import OrderCreate, OrderLineIn


# A plain Python error that carries the HTTP status the router should
# answer with. crud.py stays free of FastAPI; the router translates it.
class OrderError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


# --- products -----------------------------------------------------------

def get_products(db: Session) -> list[ProductModel]:
    return db.query(ProductModel).order_by(ProductModel.id).all()


def get_product(db: Session, product_id: int) -> ProductModel | None:
    return db.get(ProductModel, product_id)


# --- orders -------------------------------------------------------------

def get_orders(db: Session) -> list[OrderModel]:
    return (
        db.query(OrderModel)
        .options(selectinload(OrderModel.lines))
        .order_by(OrderModel.id)
        .all()
    )


def get_order(db: Session, order_id: int) -> OrderModel | None:
    return db.get(OrderModel, order_id)


def _take_from_stock(db: Session, line: OrderLineIn) -> ProductModel:
    # Shared by both versions: check the product, then decrement stock.
    product = db.get(ProductModel, line.product_id)
    if product is None:
        raise OrderError(404, f"Product {line.product_id} not found")
    if product.stock < line.quantity:
        raise OrderError(
            409,
            f"Not enough stock for {product.name}: "
            f"wanted {line.quantity}, have {product.stock}",
        )
    product.stock -= line.quantity
    return product


def place_order(db: Session, data: OrderCreate) -> OrderModel:
    """All-or-nothing: ONE transaction, ONE commit at the very end."""
    try:
        order = OrderModel(total=0)
        db.add(order)
        # flush() sends the INSERT now (so order.id exists) but does NOT
        # commit. It's still inside the transaction and can be undone.
        db.flush()

        total = 0.0
        for line in data.lines:
            product = _take_from_stock(db, line)  # may raise
            order.lines.append(
                OrderLineModel(
                    product_id=product.id,
                    quantity=line.quantity,
                    unit_price=product.price,
                )
            )
            total += product.price * line.quantity

        order.total = round(total, 2)
        db.commit()  # the only commit: everything becomes permanent together
    except Exception:
        # Anything went wrong: throw away EVERY change since the last
        # commit. The order row, its lines, and every stock decrement.
        db.rollback()
        raise
    db.refresh(order)
    return order


def place_order_unsafe(db: Session, data: OrderCreate) -> OrderModel:
    """THE BUG, on purpose: commits after every step."""
    order = OrderModel(total=0)
    db.add(order)
    db.commit()  # the empty order is now permanent

    for line in data.lines:
        product = _take_from_stock(db, line)  # may raise...
        order.lines.append(
            OrderLineModel(
                product_id=product.id,
                quantity=line.quantity,
                unit_price=product.price,
            )
        )
        order.total = round(order.total + product.price * line.quantity, 2)
        db.commit()  # ...but every line before it is already committed

    db.refresh(order)
    return order


# --- seed ---------------------------------------------------------------

def seed(db: Session) -> None:
    if db.query(ProductModel).count() == 0:
        db.add_all(
            [
                ProductModel(name="Keyboard", price=50.0, stock=10),
                ProductModel(name="Mouse", price=20.0, stock=5),
                ProductModel(name="Monitor", price=200.0, stock=1),
            ]
        )
        db.commit()
