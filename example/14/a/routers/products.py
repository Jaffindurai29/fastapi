from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, require_roles
from ids import decode_id
from models import ProductModel, UserModel
from schemas import ProductCreate, ProductOut, ProductUpdate, StockChange

router = APIRouter(prefix="/products", tags=["products"])

admin_only = require_roles("admin")


def get_product_or_404(db: Session, product_id: str, user: UserModel) -> ProductModel:
    product = db.get(ProductModel, decode_id(product_id))
    # Customers can't see hidden products at all; admins can (to un-hide).
    if product is None or (not product.is_active and user.role != "admin"):
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# ---------------------------------------------- any logged-in user ----

@router.get("", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db), user: UserModel = Depends(get_current_user)):
    query = db.query(ProductModel).order_by(ProductModel.name)
    if user.role != "admin":
        query = query.filter(ProductModel.is_active.is_(True))
    return query.all()


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: str, db: Session = Depends(get_db),
                user: UserModel = Depends(get_current_user)):
    return get_product_or_404(db, product_id, user)


# ---------------------------------------------------------- admin only ----

@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(body: ProductCreate, db: Session = Depends(get_db),
                   user: UserModel = Depends(admin_only)):
    product = ProductModel(**body.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.patch("/{product_id}", response_model=ProductOut)
def update_product(product_id: str, body: ProductUpdate, db: Session = Depends(get_db),
                   user: UserModel = Depends(admin_only)):
    product = get_product_or_404(db, product_id, user)
    # exclude_unset: only touch the fields the client actually sent.
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.patch("/{product_id}/stock", response_model=ProductOut,
              responses={400: {"description": "Stock can't go below 0"}})
def change_stock(product_id: str, body: StockChange, db: Session = Depends(get_db),
                 user: UserModel = Depends(admin_only)):
    product = get_product_or_404(db, product_id, user)
    # Lock the row so a customer's order can't change stock between our
    # read and our write.
    db.refresh(product, with_for_update=True)
    if product.stock + body.change < 0:
        raise HTTPException(status_code=400, detail=f"Only {product.stock} in stock")
    product.stock += body.change
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: str, db: Session = Depends(get_db),
                   user: UserModel = Depends(admin_only)):
    product = get_product_or_404(db, product_id, user)
    # Hide, don't delete: past orders still point at this product.
    product.is_active = False
    db.commit()
