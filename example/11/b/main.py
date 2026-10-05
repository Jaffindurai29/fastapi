from fastapi import FastAPI

import crud
from database import Base, SessionLocal, engine
from routers import categories, items

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed(db)

app = FastAPI()

app.include_router(categories.router)
app.include_router(items.router)
