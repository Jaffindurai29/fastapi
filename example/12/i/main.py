from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

import crud
from database import Base, SessionLocal, engine, get_db
from dependencies import get_current_active_user
from models import UserModel
from schemas import Token, UserOut
from security import create_access_token

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed_users(db)

# Counts requests per client IP address. Storage is in-memory by
# default: it resets on restart and isn't shared between workers. In
# production pass storage_uri="redis://localhost:6379" so every worker
# shares one set of counters.
# headers_enabled=True adds X-RateLimit-* headers to every limited
# response and Retry-After to the 429.
limiter = Limiter(key_func=get_remote_address, headers_enabled=True)

app = FastAPI()
app.state.limiter = limiter
# Turns RateLimitExceeded into a 429 JSON response.
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

AUTH_ERRORS = {
    401: {"description": "Missing, invalid or expired token"},
    403: {"description": "Inactive user"},
}


# 5 attempts per minute per IP, successful or not. slowapi needs the
# `request` parameter to find the client IP, and (because of
# headers_enabled) the `response` parameter to attach its headers to,
# since this route returns a dict rather than a Response.
@app.post("/token", response_model=Token, responses={
    401: {"description": "Incorrect username or password"},
    429: {"description": "Too many login attempts"},
})
@limiter.limit("5/minute")
def login(request: Request, response: Response,
          form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_access_token(user.username), "token_type": "bearer"}


# Not rate limited: only /token is a password-guessing target.
@app.get("/users/me", response_model=UserOut, responses=AUTH_ERRORS)
def read_me(current_user: UserModel = Depends(get_current_active_user)):
    return current_user
