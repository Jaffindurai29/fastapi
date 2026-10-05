import secrets
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, REFRESH_TOKEN_EXPIRE_DAYS, SECRET_KEY

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
        "sub": username,
        "exp": datetime.now(timezone.utc) + expires_delta,
        "type": "access",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# Same shape, three differences: lives for days, type "refresh", and a
# random "jti" (JWT ID) so two refresh tokens issued in the same second
# are still different strings.
def create_refresh_token(username: str, expires_delta: timedelta | None = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + expires_delta,
        "type": "refresh",
        "jti": secrets.token_hex(16),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_token_pair(username: str) -> dict:
    return {
        "access_token": create_access_token(username),
        "refresh_token": create_refresh_token(username),
        "token_type": "bearer",
    }


def decode_token(token: str) -> dict:
    # Checks the signature AND the exp claim. Raises jwt.InvalidTokenError
    # (or its subclass jwt.ExpiredSignatureError) if either fails.
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
