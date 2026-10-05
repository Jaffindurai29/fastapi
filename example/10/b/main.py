from fastapi import FastAPI

import crud
from database import Base, SessionLocal, engine
from routers import health, items

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed_items(db)

app = FastAPI()

# main.py no longer holds any routes. It builds the app and plugs in
# each router. Every route in items.router gets the "/items" prefix and
# the "items" tag that router was created with.
app.include_router(items.router)
app.include_router(health.router)
