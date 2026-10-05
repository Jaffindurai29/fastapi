# 8/b — HTTPException & status codes, step by step

Same `database.py`/`models.py` and `ItemCreate` as [8/a](../a/STEPS.md).
New: `ItemPatch`, two more routes, and a deliberate choice of status
code for every failure.

1. **`raise HTTPException(...)` stops the route and sends an error.**
   `status_code` is the HTTP status, and `detail` becomes the JSON body
   (`{"detail": "..."}`). The `status` module gives the numbers names,
   so the code reads as what it means:

   ```python
   raise HTTPException(
       status_code=status.HTTP_404_NOT_FOUND,
       detail=f"Item {item_id} not found",
   )
   ```

2. **`get_item_or_404` removes copy-paste.** `GET`, `PATCH` and `DELETE`
   all need "find the row or answer 404", so it lives in one helper.
   `HTTPException` is an exception, so raising it from inside a helper
   still ends the whole request. The route doesn't have to check a
   return value.

3. **`409 Conflict` for duplicates, checked *before* inserting:**

   ```python
   if crud.get_item_by_name(db, item.name) is not None:
       raise HTTPException(
           status_code=status.HTTP_409_CONFLICT,
           detail=f"An item named '{item.name}' already exists",
       )
   ```

   This fixes 8/a's `500`. The body is perfectly valid (so it's not
   `422`), but it conflicts with existing data. The `unique=True`
   column stays as a safety net in case two requests race each other.

4. **`ItemPatch` — every field optional, same rules.** `PATCH` sends
   only what changed, so every field has `default=None`. `Field(gt=0)`
   and the others still apply to whatever *is* sent.

5. **`model_dump(exclude_unset=True)` — what did the client actually
   send?**

   ```python
   changes = patch.model_dump(exclude_unset=True)
   ```

   For a body of `{"price": 899}`, this is `{"price": 899}`, **not**
   `{"name": None, "price": 899, "quantity": None}`. That's how one
   generic `crud.update_item` can apply any combination of fields with
   `setattr`. An empty `{}` gives an empty dict, which is a `400`: the
   request is valid JSON, but it asks for nothing.

6. **`null` is rejected explicitly.** `{"price": null}` *is* "set", so
   it survives `exclude_unset`. The columns are `nullable=False`, so the
   route answers `400` instead of letting the database crash.

7. **Renaming checks for conflicts too**, but only when the name
   actually changes. `PATCH {"name": "Laptop"}` on the Laptop itself is
   fine.

8. **A business rule is also a `409`.** `DELETE` refuses while
   `quantity > 0`. Nothing about the request is malformed. It conflicts
   with the item's current state.

9. **`DELETE` returns `204 No Content`**, and the function returns
   nothing. A `204` has no body by definition.
