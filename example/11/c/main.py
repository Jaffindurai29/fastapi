from fastapi import FastAPI

import crud
from database import Base, SessionLocal, engine
from routers import items, tags

# rel_categories and rel_items already exist if you ran 11/a or 11/b, so
# create_all skips them and only creates rel_tags and rel_item_tags.
Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed(db)

app = FastAPI()

app.include_router(items.router)
app.include_router(tags.router)
