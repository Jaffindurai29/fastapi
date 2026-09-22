# 6/e — DELETE (MySQL), step by step

Same `database.py`/`models.py` as [6/a](../a/STEPS.md) (same shared
`items` table) — no `schemas.py` here, since `DELETE` has no request
body. The delete logic lives in `crud.py`:

```python
# crud.py
def get_item(db: Session, item_id: int) -> ItemModel | None:
    return db.get(ItemModel, item_id)


def delete_item(db: Session, item_id: int) -> bool:
    row = get_item(db, item_id)
    if row is None:
        return False
    db.delete(row)
    db.commit()
    return True


# main.py
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_item(db, item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
```

1. **Look the row up first** — same `404`-if-missing pattern as every
   other route in this topic, except `crud.delete_item` reports the
   miss by returning `False` (there's no `row` left to hand back after
   a delete) instead of `None` — `main.py` checks `if not deleted:`
   instead of `if row is None:`.
2. **`db.delete(row)` then `db.commit()`** — stages the deletion, then
   writes it.
3. **Unlike the array topic**, deleting a row here never shifts any
   other row's `id` — MySQL's auto-increment `id` is a stable identity,
   not a position in a list. That's one of the real advantages of a
   database over an in-memory array for anything that needs to survive
   deletions predictably.
