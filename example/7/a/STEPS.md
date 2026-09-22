# 7/a — MySQL backend, full CRUD + CORS, step by step

This file is [topic 6](../../6)'s five routes (6/a=GET, 6/b=POST,
6/c=PUT, 6/d=PATCH, 6/e=DELETE) combined into one running app, plus
CORS — the same relationship [5/a](../../5/a) has to
[topic 4](../../4). If you've already read topic 6's STEPS.md files,
nothing about the database logic itself is new here; this walks through
what's added on top.

1. **Same `database.py` as every topic 6 folder**, and the same
   layered split — `database.py`/`models.py`/`schemas.py`/`crud.py`/
   `main.py` — see [6/a's Files section](../../6/a/README.md#files).
   `models.py`'s `ItemModel` is the one thing that differs from topic 6:
   its table is `crud_react_items`, not the `items` table topic 6's
   five folders share, so this topic's demo data never collides with
   topic 6's.

2. **`crud.py` has all six functions** — one per verb (`get_items`,
   `get_item`, `create_item`, `replace_item`, `update_item`,
   `delete_item`), plus `seed_items` — the union of what each topic 6
   folder had on its own. **`main.py` declares all five routes on the
   same `app`**, each one just calling into `crud.py` and translating a
   miss into `HTTPException(404, ...)`:

   ```python
   @app.get("/items")
   def list_items(db: Session = Depends(get_db)):
       return [{"id": row.id, "value": row.value} for row in crud.get_items(db)]

   @app.get("/items/{item_id}")
   def get_item(item_id: int, db: Session = Depends(get_db)):
       row = crud.get_item(db, item_id)
       if row is None:
           raise HTTPException(status_code=404, detail="Item not found")
       return {"id": row.id, "value": row.value}

   @app.post("/items", status_code=status.HTTP_201_CREATED)
   def create_item(item: ItemRequest, db: Session = Depends(get_db)):
       row = crud.create_item(db, item)
       return {"id": row.id, "value": row.value}

   @app.put("/items/{item_id}")
   def replace_item(item_id: int, item: ItemRequest, db: Session = Depends(get_db)):
       row = crud.replace_item(db, item_id, item)
       if row is None:
           raise HTTPException(status_code=404, detail="Item not found")
       return {"id": row.id, "value": row.value}

   @app.patch("/items/{item_id}")
   def update_item(item_id: int, patch: ItemPatch, db: Session = Depends(get_db)):
       row = crud.update_item(db, item_id, patch)
       if row is None:
           raise HTTPException(status_code=404, detail="Item not found")
       return {"id": row.id, "value": row.value}

   @app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
   def delete_item(item_id: int, db: Session = Depends(get_db)):
       deleted = crud.delete_item(db, item_id)
       if not deleted:
           raise HTTPException(status_code=404, detail="Item not found")
   ```

   **Why combine them:** a real frontend needs to `GET`, `POST`, `PUT`,
   `PATCH`, and `DELETE` against the *same* running server — five
   separate standalone apps on five different ports wouldn't let one
   React page talk to all of them at once. That's also why this
   folder's `crud.py` is one file with six functions instead of five
   folders each with one or two — one app, one module per layer.

3. **The one genuinely new piece: CORS**, imported and registered once,
   right after creating `app` — identical to
   [5/a's STEPS.md](../../5/a/STEPS.md), just added to the MySQL-backed
   app instead of the array-backed one:

   ```python
   from fastapi.middleware.cors import CORSMiddleware

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

4. **Difference from 5/a that matters for the frontend:** every
   response here includes a real database `id`
   (`{"id": 1, "value": "first"}`), not an array position
   (`{"index": 0, "value": "first"}`). That's why
   [7/react](../react) addresses rows by `id` — see its
   [STEPS.md](../react/STEPS.md) for exactly what that changes on the
   frontend side.
