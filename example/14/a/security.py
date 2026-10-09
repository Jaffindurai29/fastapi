from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, REFRESH_TOKEN_EXPIRE_DAYS, SECRET_KEY

# ------------------------------------------------------------ HASHING ----
# One-way. Used for passwords: we can CHECK a password, never read it back.
# (Two-way encryption for phone/address lives in encryption.py.)

password_hash = PasswordHash.recommended()  # Argon2


def hash_password(password: str) -> str:
    # A fresh random salt every call: same password, different hash.
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


# ---------------------------------------------------------------- JWT ----

def _create_token(username: str, token_type: str, expires: timedelta, **extra) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,     # who the token is about
        "type": token_type,  # "access" or "refresh", so one can't pose as the other
        "iat": now,          # issued at
        "exp": now + expires,  # PyJWT rejects the token after this moment
        **extra,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(username: str, role: str) -> str:
    # The role is in the token only so the FRONTEND can pick a menu.
    # The backend never trusts it: dependencies.py reads the role from
    # the database on every request.
    return _create_token(
        username, "access", timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), role=role
    )


def create_refresh_token(username: str) -> str:
    return _create_token(username, "refresh", timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))


def decode_token(token: str, expected_type: str) -> str | None:
    """The username, or None if the token is expired, tampered with, or the wrong type."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:  # covers ExpiredSignatureError too
        return None
    if payload.get("type") != expected_type:
        return None
    return payload.get("sub")
