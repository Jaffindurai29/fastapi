from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

import crud
from config import settings
from database import Base, SessionLocal, engine
from rate_limit import limiter
from routers import auth, notes, users

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed(db)

# CHECKLIST: no interactive docs in production. /docs is great while
# building, but in production it hands strangers a map of every route.
docs_off = settings.is_production
app = FastAPI(
    title="Secure notes",
    docs_url=None if docs_off else "/docs",
    redoc_url=None if docs_off else "/redoc",
    openapi_url=None if docs_off else "/openapi.json",
)

# slowapi looks for the limiter on app.state, and this handler turns a
# blocked request into a 429 response.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CHECKLIST: CORS only from settings. Never allow_origins=["*"] together
# with allow_credentials=True (browsers reject it, and it would let any
# site make logged-in requests). We send tokens in the Authorization
# header, not cookies, so credentials aren't needed at all.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


# CHECKLIST: security headers on every response.
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    # Don't let the browser guess a different content type than we sent.
    response.headers["X-Content-Type-Options"] = "nosniff"
    # Don't allow this API to be framed by another site (clickjacking).
    response.headers["X-Frame-Options"] = "DENY"
    # Don't leak our URLs (which might contain ids) to other sites.
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(notes.router)
