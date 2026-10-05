from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import crud
from database import Base, SessionLocal, engine, get_db
from dependencies import get_current_user, require_role
from models import UserModel
from schemas import RoleUpdate, Token, UserOut
from security import create_access_token

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed_users(db)

app = FastAPI()

NOT_FOUND = {404: {"description": "User not found"}}


@app.post("/token", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form.username, form.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_access_token(user.username, user.role), "token_type": "bearer"}


# Any logged-in user, whatever the role.
@app.get("/users/me", response_model=UserOut)
def read_me(user: UserModel = Depends(get_current_user)):
    return user


# Admin only. The dependency runs first: a plain "user" gets 403 and
# this function body never executes.
@app.get("/admin/users", response_model=list[UserOut])
def list_users(
    admin: UserModel = Depends(require_role("admin")), db: Session = Depends(get_db)
):
    return crud.get_users(db)


@app.patch("/admin/users/{user_id}/role", response_model=UserOut, responses=NOT_FOUND)
def change_role(
    user_id: int,
    body: RoleUpdate,
    admin: UserModel = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    user = crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.set_role(db, user, body.role)


@app.delete("/admin/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, responses=NOT_FOUND)
def delete_user(
    user_id: int,
    admin: UserModel = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    # Guard against locking yourself out by accident.
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account")
    user = crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    crud.delete_user(db, user)
