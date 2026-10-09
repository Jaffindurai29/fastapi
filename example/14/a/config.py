import os

from dotenv import load_dotenv

load_dotenv()

# Every secret below has a DEV-ONLY default so the lesson runs with zero
# setup. These defaults are public (they're in git), so anything they
# sign or encrypt is readable by anyone with this repo. For anything
# real, set all three in .env (see .env.example) and never commit them.

# Signs JWTs (12/b).
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-change-me-in-production-0123456789")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Encrypts order phone + address (12/g).
FERNET_KEY = os.getenv("FERNET_KEY", "Hq1oQZm3T7V4YkX0sKcN8bWfPuR2dJgLaEyC6iMh5tA=")

# Turns database ids into public ids (12/h).
SQIDS_ALPHABET = os.getenv(
    "SQIDS_ALPHABET", "kR3vXq8LbN1mZ7cTj0sWfYp4HdG2uEoA9iVnKrQ6tBhS5aCgPxMlUyJeFwDzIO"
)
SQIDS_MIN_LENGTH = 8

# Which browser origins may call the API: the Vite dev server of 14/react.
CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
