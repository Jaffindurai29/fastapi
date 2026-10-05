import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from pwdlib import PasswordHash

from config import settings

ALGORITHM = "HS256"

# Argon2 with sensible defaults (salted, deliberately slow).
password_hash = PasswordHash.recommended()

# Used when the username doesn't exist, so a failed login takes the same
# time either way and the response time can't reveal which usernames exist.
DUMMY_HASH = password_hash.hash("dummy-password-for-timing")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def _create_token(username: str, token_type: str, expires_delta: timedelta, extra: dict | None = None) -> str:
    payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + expires_delta,
        "type": token_type,
        **(extra or {}),
    }
    # Note what is NOT in here: no role, no password, nothing secret.
    # Anyone holding the token can base64-decode and read the payload.
    return jwt.encode(payload, settings.secret_key.get_secret_value(), algorithm=ALGORITHM)


def create_access_token(username: str) -> str:
    return _create_token(username, "access", timedelta(minutes=settings.access_token_expire_minutes))


def create_refresh_token(username: str) -> tuple[str, str]:
    """Returns (token, jti). The jti is stored in the database so the
    token can be rotated/revoked."""
    jti = uuid.uuid4().hex
    token = _create_token(
        username, "refresh", timedelta(days=settings.refresh_token_expire_days), {"jti": jti}
    )
    return token, jti


def credentials_error(detail: str = "Could not validate credentials") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def decode_token(token: str, expected_type: str) -> dict:
    """Checks signature + expiry + type. Raises 401 on any problem."""
    try:
        # algorithms=[...] is required: never let the token pick its own
        # algorithm (the classic "alg": "none" attack).
        payload = jwt.decode(token, settings.secret_key.get_secret_value(), algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise credentials_error("Token expired")
    except jwt.InvalidTokenError:
        raise credentials_error()
    # A refresh token must not work as an access token, and vice versa.
    if payload.get("type") != expected_type or not payload.get("sub"):
        raise credentials_error()
    return payload
