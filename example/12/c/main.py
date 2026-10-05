from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import crud
from database import Base, SessionLocal, engine, get_db
from dependencies import get_current_active_user
from models import UserModel
from schemas import Token, UserOut
from security import create_access_token

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed_users(db)

app = FastAPI()

# Demo data, kept in memory: this lesson is about the lock, not the data.
ITEMS = [
    {"id": 1, "name": "Laptop"},
    {"id": 2, "name": "Mouse"},
    {"id": 3, "name": "Monitor"},
]

AUTH_ERRORS = {
    401: {"description": "Missing, invalid or expired token"},
    403: {"description": "Inactive user"},
}


@app.post("/token", response_model=Token,
          responses={401: {"description": "Incorrect username or password"}})
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_access_token(user.username), "token_type": "bearer"}


# No dependency: anyone can call it.
@app.get("/public")
def public():
    return {"message": "Anyone can see this"}


# The route never touches the token. If the dependency returns, the
# user is real, active, and their token is valid.
@app.get("/users/me", response_model=UserOut, responses=AUTH_ERRORS)
def read_me(current_user: UserModel = Depends(get_current_active_user)):
    return current_user


@app.get("/items", responses=AUTH_ERRORS)
def list_items(current_user: UserModel = Depends(get_current_active_user)):
    return ITEMS
