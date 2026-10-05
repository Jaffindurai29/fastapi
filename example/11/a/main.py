from fastapi import FastAPI

import crud
from database import Base, SessionLocal, engine
from routers import categories, items

# Creates BOTH tables, parent first: create_all reads the ForeignKey to
# work out that rel_categories must exist before rel_items.
Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed(db)

app = FastAPI()

# One router module per resource; main.py just plugs them in.
app.include_router(categories.router)
app.include_router(items.router)
