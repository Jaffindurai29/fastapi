# 6/d — PATCH (MySQL), step by step

Same `database.py`/`models.py` as [6/a](../a/STEPS.md) (same shared
`items` table). Same "required vs. optional" distinction as the
[array topic's PATCH](../../4/d/STEPS.md), now split across
`schemas.py`, `crud.py`, and `main.py`:

```python
# schemas.py
class ItemPatch(BaseModel):
    value: Optional[str] = None


# crud.py
def get_item(db: Session, item_id: int) -> ItemModel | None:
    return db.get(ItemModel, item_id)


def update_item(db: Session, item_id: int, patch: ItemPatch) -> ItemModel | None:
    row = get_item(db, item_id)
    if row is None:
        return None
    if patch.value is not None:
        row.value = patch.value
    db.commit()
    db.refresh(row)
    return row


# main.py
@app.patch("/items/{item_id}")
def update_item(item_id: int, patch: ItemPatch, db: Session = Depends(get_db)):
    row = crud.update_item(db, item_id, patch)
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": row.id, "value": row.value}
```

1. **`ItemPatch.value` is optional** — unlike [6/c](../c/STEPS.md)'s
   `ItemRequest`, where `value` is required.
2. **`if patch.value is not None: row.value = patch.value`** — only
   updates the row if the client actually sent a value; an empty body
   (`{}`) leaves it untouched.
3. **`crud.update_item` returns `None` on a missing ID**, same pattern
   as [6/c](../c/STEPS.md)'s `replace_item` — `main.py` is the only
   place that turns that into `HTTPException(404, ...)`.
