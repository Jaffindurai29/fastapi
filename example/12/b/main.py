import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import crud
from database import Base, SessionLocal, engine, get_db
from schemas import Token
from security import create_access_token, decode_token

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed_users(db)

app = FastAPI()


# OAuth2PasswordRequestForm reads FORM fields `username` and `password`
# (not JSON). That's what the OAuth2 spec says, and it's what the
# "Authorize" button in /docs sends.
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


# Teaching route: what's inside a token, and is it genuine?
@app.get("/token/inspect", responses={400: {"description": "Not a JWT at all"}})
def inspect_token(token: str):
    try:
        # No key needed: the header and payload are only base64.
        header = jwt.get_unverified_header(token)
        payload = jwt.decode(token, options={"verify_signature": False})
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Not a JWT")

    try:
        # The real check: signature + expiry, using SECRET_KEY.
        verified = decode_token(token)
        return {"header": header, "payload": payload, "valid": True, "verified_payload": verified}
    except jwt.InvalidTokenError as exc:
        return {"header": header, "payload": payload, "valid": False, "error": str(exc)}
