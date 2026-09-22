# 6/b — POST (MySQL), step by step

Same `database.py`/`models.py` as [6/a](../a/STEPS.md) (same shared
`items` table). What's new here is `schemas.py`'s `ItemRequest`,
`crud.py`'s `create_item`, and the route in `main.py` that calls it:

```python
# schemas.py
class ItemRequest(BaseModel):
    value: str


# crud.py
def create_item(db: Session, item: ItemRequest) -> ItemModel:
    row = ItemModel(value=item.value)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


# main.py
@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(item: ItemRequest, db: Session = Depends(get_db)):
    row = crud.create_item(db, item)
    return {"id": row.id, "value": row.value}
```

1. **`ItemModel(value=item.value)`** — builds a new ORM object in
   memory; nothing is written to the database yet.
2. **`db.add(row)`** — stages it for insertion.
3. **`db.commit()`** — actually writes it, and this is the point where
   MySQL assigns the real auto-incrementing `id`.
4. **`db.refresh(row)`** — pulls that generated `id` back into `row`
   from the database, so the function can return it. Without this
   step, `row.id` would still be `None`.
5. **`crud.create_item` returns the ORM object itself**, not a dict —
   `main.py`'s route is what shapes it into `{"id": ..., "value": ...}`
   for the response. Keeping `crud.py` free of any HTTP-shaped return
   value is what makes it reusable from anywhere, not just this one
   route.
