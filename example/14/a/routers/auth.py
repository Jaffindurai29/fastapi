from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud
from database import get_db
from dependencies import get_current_user
from schemas import LoginRequest, RefreshRequest, TokenPair, UserCreate, UserOut
from security import create_access_token, create_refresh_token, decode_token

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED,
             responses={409: {"description": "Username already taken"}})
def register(user: UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, user.username) is not None:
        raise HTTPException(status_code=409, detail="Username already taken")
    # No "role" field in UserCreate on purpose: nobody can sign up as admin.
    return crud.create_user(db, user.username, user.password)


@router.post("/login", response_model=TokenPair,
             responses={401: {"description": "Incorrect username or password"}})
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
    # The password is checked once, here. From now on the client proves
    # who it is with the access token instead.
    return TokenPair(
        access_token=create_access_token(user.username, user.role),
        refresh_token=create_refresh_token(user.username),
    )


@router.post("/refresh", response_model=TokenPair,
             responses={401: {"description": "Refresh token invalid or expired"}})
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    username = decode_token(body.refresh_token, expected_type="refresh")
    user = crud.get_user_by_username(db, username) if username else None
    if user is None:
        # Refresh token is dead (or the user was deleted): log in again.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalid or expired",
        )
    # The new access token carries the CURRENT role, so a promotion shows
    # up in the frontend's menu after the next refresh.
    return TokenPair(
        access_token=create_access_token(user.username, user.role),
        refresh_token=body.refresh_token,
    )


@router.get("/me", response_model=UserOut,
            responses={401: {"description": "Access token invalid or expired"}})
def me(user=Depends(get_current_user)):
    return user
