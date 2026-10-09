from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import crud
import models  # noqa: F401  (registers every table with Base before create_all)
from config import CORS_ORIGINS
from database import Base, SessionLocal, engine
from routers import auth, orders, products, users

# Four new minishop_* tables, so create_all is enough here. Changing a table
# that already exists would need a migration (topic 13).
Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed(db)

app = FastAPI(title="Mini shop")

# Only the 14/react dev server may call this API from a browser. Tokens
# travel in the Authorization header, not cookies, so no credentials.
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(users.router)
