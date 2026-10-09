from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from dependencies import require_roles
from ids import decode_id
from models import UserModel
from schemas import RoleUpdate, UserOut

# Every route in this file is admin-only, so the check goes on the router.
router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(require_roles("admin"))])


@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(UserModel).order_by(UserModel.id).all()


@router.patch("/{user_id}/role", response_model=UserOut,
              responses={400: {"description": "You can't change your own role"}})
def change_role(user_id: str, body: RoleUpdate, db: Session = Depends(get_db),
                admin: UserModel = Depends(require_roles("admin"))):
    user = db.get(UserModel, decode_id(user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # Stops the last admin from locking everyone out by demoting themselves.
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="You can't change your own role")
    user.role = body.role
    db.commit()
    db.refresh(user)
    return user
