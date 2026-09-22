# 6/c — PUT (MySQL), step by step

Same `database.py`/`models.py` as [6/a](../a/STEPS.md) (same shared
`items` table), same `schemas.py` `ItemRequest` as
[6/b](../b/STEPS.md). The update logic lives in `crud.py`; `main.py`'s
route just calls it and translates a miss into a `404`:

```python
# crud.py
def get_item(db: Session, item_id: int) -> ItemModel | None:
    return db.get(ItemModel, item_id)


def replace_item(db: Session, item_id: int, item: ItemRequest) -> ItemModel | None:
    row = get_item(db, item_id)
    if row is None:
        return None
    row.value = item.value
    db.commit()
    db.refresh(row)
    return row


# main.py
@app.put("/items/{item_id}")
def replace_item(item_id: int, item: ItemRequest, db: Session = Depends(get_db)):
    row = crud.replace_item(db, item_id, item)
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": row.id, "value": row.value}
```

1. **`crud.replace_item` looks the row up first** — `get_item(db,
   item_id)` (itself just `db.get(ItemModel, item_id)`) returns `None`
   if that ID doesn't exist, and `replace_item` returns `None` right
   back rather than raising anything — `crud.py` never knows about
   HTTP status codes.
2. **`main.py` is what turns that `None` into `HTTPException(404,
   ...)`** — the same "crud stays HTTP-agnostic, main.py raises"
   split used everywhere in this topic.
3. **`row.value = item.value`** — this looks like a plain attribute
   assignment because it is one. SQLAlchemy's ORM tracks the change on
   `row` automatically; nothing needs to be re-added to the session.
4. **`db.commit()`** writes the change; **`db.refresh(row)`** makes sure
   `row` reflects exactly what's now in the database before it's
   returned.
