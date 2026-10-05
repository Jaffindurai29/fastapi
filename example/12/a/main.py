from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

import crud
from database import Base, SessionLocal, engine, get_db
from schemas import LoginRequest, UserCreate, UserOut
from security import hash_password, verify_password

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed_users(db)

app = FastAPI()


@app.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED,
          responses={409: {"description": "Username already taken"}})
def register(user: UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, user.username) is not None:
        raise HTTPException(status_code=409, detail="Username already taken")
    return crud.create_user(db, user.username, user.password)


@app.post("/login", responses={401: {"description": "Incorrect username or password"}})
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = crud.authenticate(db, body.username, body.password)
    if user is None:
        # Same message for "no such user" and "wrong password", so an
        # attacker can't use this route to discover which usernames exist.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # No token yet: the client learns "yes, that's right" and nothing more.
    # 12/b turns this into a JWT the client can send on later requests.
    return {"message": "Login successful", "username": user.username}


@app.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return crud.get_users(db)


# Teaching route: hash the same password twice to show the salt at work.
# (Never put a real password in a URL; it ends up in server logs.)
@app.get("/hash-demo")
def hash_demo(password: str = "secret"):
    first = hash_password(password)
    second = hash_password(password)
    return {
        "password": password,
        "hash_1": first,
        "hash_2": second,
        "hashes_equal": first == second,
        "verify_hash_1": verify_password(password, first),
        "verify_hash_2": verify_password(password, second),
        "verify_wrong_password": verify_password(password + "x", first),
    }
