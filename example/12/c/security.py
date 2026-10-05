from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY

# Argon2, exactly as in 12/a.
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_access_token(username: str, expires_delta: timedelta | None = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": username,  # who the token is about (the "subject")
        "exp": datetime.now(timezone.utc) + expires_delta,  # stored as a Unix timestamp
        "type": "access",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    # Checks the signature AND the exp claim. Raises jwt.InvalidTokenError
    # (or its subclass jwt.ExpiredSignatureError) if either fails.
    # algorithms= is a whitelist: never let the token pick its own.
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
