import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import crud
from database import Base, SessionLocal, engine, get_db
from dependencies import credentials_error, get_current_active_user
from models import UserModel
from schemas import RefreshRequest, TokenPair, UserOut
from security import create_token_pair, decode_token

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed_users(db)

app = FastAPI()

AUTH_ERRORS = {
    401: {"description": "Missing, invalid or expired token"},
    403: {"description": "Inactive user"},
}


@app.post("/token", response_model=TokenPair,
          responses={401: {"description": "Incorrect username or password"}})
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_token_pair(user.username)


# Trade a refresh token for a new pair. No password needed: that's the
# whole point. The refresh token goes in a JSON body, not the
# Authorization header, so it can never be mistaken for an access token.
@app.post("/refresh", response_model=TokenPair,
          responses={401: {"description": "Invalid or expired refresh token"}})
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = decode_token(body.refresh_token)
    except jwt.ExpiredSignatureError:
        raise credentials_error("Refresh token has expired")
    except jwt.InvalidTokenError:
        raise credentials_error("Invalid refresh token")

    # An access token is signed with the same key, so the signature alone
    # can't tell them apart. The type claim can.
    if payload.get("type") != "refresh":
        raise credentials_error("Invalid refresh token")

    # Re-check the account: it may have been deleted or deactivated
    # since the refresh token was issued.
    user = crud.get_user_by_username(db, payload.get("sub") or "")
    if user is None or not user.is_active:
        raise credentials_error("Invalid refresh token")

    # Rotation: hand out a NEW refresh token too, so an active client's
    # refresh token keeps moving and never reaches its 7-day expiry.
    return create_token_pair(user.username)


@app.get("/users/me", response_model=UserOut, responses=AUTH_ERRORS)
def read_me(current_user: UserModel = Depends(get_current_active_user)):
    return current_user
