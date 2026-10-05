from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import crud
from config import settings
from database import get_db
from models import UserModel
from rate_limit import limiter
from schemas import RefreshRequest, Token, UserCreate, UserOut
from security import (
    DUMMY_HASH,
    create_access_token,
    create_refresh_token,
    credentials_error,
    decode_token,
    verify_password,
)

router = APIRouter(tags=["auth"])


def issue_tokens(db: Session, user: UserModel) -> Token:
    refresh_token, jti = create_refresh_token(user.username)
    crud.save_refresh_token(db, jti, user.id)
    return Token(access_token=create_access_token(user.username), refresh_token=refresh_token)


# CHECKLIST: rate-limited login. The 6th attempt within a minute from
# the same IP gets 429 Too Many Requests, which makes guessing passwords
# by brute force impractical. slowapi needs the `request` argument.
@router.post("/token", response_model=Token)
@limiter.limit(settings.login_rate_limit)
def login(request: Request, form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form.username)
    # Hash-check even when the user doesn't exist, so both failures take
    # the same time.
    password_ok = verify_password(form.password, user.hashed_password if user else DUMMY_HASH)
    # CHECKLIST: generic login error. "No such user" vs "wrong password"
    # would tell an attacker which usernames exist.
    if user is None or not password_ok or not user.is_active:
        raise credentials_error("Incorrect username or password")
    return issue_tokens(db, user)


@router.post("/refresh", response_model=Token)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_token(body.refresh_token, expected_type="refresh")
    stored = crud.get_refresh_token(db, payload.get("jti", ""))
    # Rotation: each refresh token works exactly once. Reusing an old one
    # (e.g. a stolen copy) fails here.
    if stored is None or stored.revoked:
        raise credentials_error("Refresh token is no longer valid")
    user = crud.get_user_by_username(db, payload["sub"])
    if user is None or not user.is_active:
        raise credentials_error()
    crud.revoke_refresh_token(db, stored)
    return issue_tokens(db, user)


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, data.username) is not None:
        raise HTTPException(status_code=409, detail="Username already taken")
    # Always "user". Admins are made by an admin, not by signing up.
    return crud.create_user(db, data, role="user")
