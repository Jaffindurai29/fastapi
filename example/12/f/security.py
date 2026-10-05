from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_access_token(username: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # "role" is informational only (handy for a frontend that wants to
    # show or hide an Admin button). The server never trusts it: see
    # get_current_user in dependencies.py.
    payload = {"sub": username, "role": role, "exp": expire, "type": "access"}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """Return the username inside a valid access token, else None."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:  # bad signature, expired, garbage...
        return None
    if payload.get("type") != "access":
        return None
    return payload.get("sub")
