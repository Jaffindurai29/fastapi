from pwdlib import PasswordHash

# Argon2 with sensible defaults. (passlib, used in older tutorials,
# no longer works on Python 3.13+; pwdlib is its modern replacement.)
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    # One-way: a fresh random salt is mixed in every call, so the same
    # password gives a different hash each time.
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    # Re-hashes the attempt using the salt stored inside `hashed` and
    # compares. The original password is never recovered.
    return password_hash.verify(password, hashed)
