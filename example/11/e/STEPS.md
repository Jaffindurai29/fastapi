# 11/e — Soft delete, step by step

Same `database.py` as [6/a](../../6/a/STEPS.md). One table, one new
column, and a rule that every query has to follow.

1. **Why not just delete?**
   - **Undo.** "I deleted the wrong thing" is one of the most common
     support requests. With a real `DELETE` the answer is "restore last
     night's backup". With a soft delete it's one `UPDATE`.
   - **Audit.** You can still see what existed and when it was removed.
   - **References from other tables.** An old order line (see
     [11/d](../d/STEPS.md)) points at a product. Hard-deleting the
     product either fails on the foreign key or leaves the line pointing
     at nothing. A soft-deleted product stays in the table, so old
     orders still resolve, while the shop stops listing it.

2. **`models.py` — one nullable timestamp:**

   ```python
   deleted_at = Column(DateTime, nullable=True, default=None)
   ```

   `NULL` means live. A timestamp means "deleted at this moment". A
   timestamp instead of a `is_deleted` true/false flag costs nothing
   extra and also records *when*.

3. **`crud.py` — the soft delete is an `UPDATE`:**

   ```python
   def soft_delete_item(db: Session, row: SoftItemModel) -> None:
       # An UPDATE, not a DELETE. func.now() lets the database fill in the
       # time, same as server_default in 8/d.
       row.deleted_at = func.now()
       db.commit()
   ```

   `func.now()` lets the database fill in the time, like
   `server_default=func.now()` in [8/d](../../8/d/STEPS.md). The route
   still answers `204 No Content`; to the client it's a delete.

4. **`crud.py` — the filter every normal read needs:**

   ```python
   def get_items(db: Session, include_deleted: bool = False) -> list[SoftItemModel]:
       query = db.query(SoftItemModel)
       if not include_deleted:
           # The price of soft delete: EVERY normal query needs this filter.
           # Forget it once and "deleted" rows show up again.
           query = query.filter(SoftItemModel.deleted_at.is_(None))
       return query.order_by(SoftItemModel.id).all()
   ```

   `.is_(None)` becomes `WHERE deleted_at IS NULL`. (Writing
   `== None` also works but linters flag it; `= NULL` in SQL never
   matches anything, which is why SQL has `IS NULL`.)

   `include_deleted: bool = False` is a query parameter. FastAPI turns
   `?include_deleted=true` (also `1`, `yes`, `on`) into `True`.

5. **`crud.py` — two ways to fetch one row:**

   ```python
   def get_item(db: Session, item_id: int) -> SoftItemModel | None:
       """Any row, deleted or not. Used by restore and permanent delete."""
       return db.get(SoftItemModel, item_id)


   def get_live_item(db: Session, item_id: int) -> SoftItemModel | None:
       """Only a row that isn't soft-deleted. What normal reads use."""
       return (
           db.query(SoftItemModel)
           .filter(SoftItemModel.id == item_id, SoftItemModel.deleted_at.is_(None))
           .first()
       )
   ```

   `db.get()` knows nothing about soft delete; it returns the row either
   way. That's exactly what restore needs, and exactly what a normal
   `GET` must **not** use.

6. **`routers/items.py` — deleted looks like missing:**

   ```python
   row = crud.get_live_item(db, item_id)
   if row is None:
       raise HTTPException(status_code=404, detail="Item not found")
   ```

   `GET` and `DELETE` treat a soft-deleted item as gone. Deleting it a
   second time is also a `404`: there's nothing (live) at that URL.

7. **`routers/items.py` — restore:**

   ```python
   row = crud.get_item(db, item_id)  # deleted rows included on purpose
   if row is None:
       raise HTTPException(status_code=404, detail="Item not found")
   if row.deleted_at is None:
       raise HTTPException(status_code=409, detail="Item is not deleted")
   return crud.restore_item(db, row)
   ```

   `404` if there's no row at all (never existed, or purged). `409` if
   it exists but is live: the request makes sense, the current state
   doesn't allow it.

8. **`routers/items.py` — a real delete still exists:**

   ```python
   row = crud.get_item(db, item_id)
   ...
   crud.hard_delete_item(db, row)
   ```

   Sometimes data really must go: a user asks for their data to be
   erased, or a cleanup job purges rows soft-deleted more than 30 days
   ago. `/permanent` runs a real `DELETE` on live and soft-deleted rows
   alike. In a real app this is usually admin-only.

9. **The cost.**
   - **Every query must filter.** Every list, every lookup, every count,
     every join from another table. Forget `deleted_at IS NULL` once and
     "deleted" data shows up again. Some projects hide this behind a
     helper (like `get_live_item` here) or a database view, but it never
     goes away completely.
   - **Unique constraints get tricky.** If `name` were `unique=True`,
     soft-deleting "Mouse" would still block creating a new "Mouse": the
     old row is still there. Fixes all have trade-offs: make the unique
     key `(name, deleted_at)` (but MySQL allows many `NULL`s in a unique
     index, so two *live* "Mouse" rows would slip through), or check
     uniqueness in code among live rows only. That's why this lesson's
     `name` isn't unique.
   - **The table only grows.** Deleted rows still take space and slow
     scans, which is why a purge job usually comes with it.

   Use soft delete where undo, history, or references matter (orders,
   users, documents). For throwaway data (sessions, temp files), a real
   delete is simpler.
