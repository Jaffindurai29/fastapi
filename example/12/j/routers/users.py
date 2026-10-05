from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import crud
from database import get_db
from dependencies import get_current_user, require_role
from models import UserModel
from schemas import UserOut

router = APIRouter(tags=["users"])


@router.get("/users/me", response_model=UserOut)
def read_me(user: UserModel = Depends(get_current_user)):
    return user  # the ORM row has hashed_password; UserOut drops it


@router.get("/admin/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), admin: UserModel = Depends(require_role("admin"))):
    return crud.get_users(db)
