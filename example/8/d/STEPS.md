# 8/d — `response_model` & status codes, step by step

Same `database.py` as [6/a](../../6/a/STEPS.md). The point of this
lesson is the split between what comes **in** (`ItemCreate`) and what
goes **out** (`ItemOut`).

1. **`models.py` — two new columns:** `supplier_cost`, internal data the
   client must never see, and `created_at`, which the database fills in
   itself:

   ```python
   supplier_cost = Column(Float, nullable=False, default=0)
   created_at = Column(DateTime, nullable=False, server_default=func.now())
   ```

2. **`schemas.py` — separate input and output models.** `ItemCreate`
   includes `supplier_cost`, because an admin types it in. `ItemOut`
   doesn't include it, and it adds `id` and `created_at`, which the
   client never sends:

   ```python
   class ItemOut(BaseModel):
       model_config = ConfigDict(from_attributes=True)

       id: int
       name: str
       price: float
       quantity: int
       created_at: datetime
   ```

3. **`from_attributes=True`** lets Pydantic read `row.name` off a
   SQLAlchemy object. Without it, Pydantic only knows how to read dicts,
   and returning a row fails validation.

4. **`response_model=ItemOut` filters the output:**

   ```python
   @app.get("/items/{item_id}", response_model=ItemOut, responses=NOT_FOUND)
   def get_item(item_id: int, db: Session = Depends(get_db)):
       row = crud.get_item(db, item_id)
       if row is None:
           raise HTTPException(status_code=404, detail="Item not found")
       return row  # still has supplier_cost — ItemOut filters it out
   ```

   The route returns the *full* row. FastAPI passes it through
   `ItemOut`, keeps only the listed fields, and checks their types. If
   you add a secret column to the table later, it **can't** leak by
   accident, because it's not in `ItemOut`. That's why this is safer
   than hand-built dicts: with dicts, you'd have to remember to leave it
   out in every single route.

5. **Lists work the same way:** `response_model=list[ItemOut]`.

6. **`crud.create_item` uses `ItemModel(**item.model_dump())`.** The
   field names in `ItemCreate` match the column names, so the whole body
   unpacks straight into the model.

7. **`status_code=` on the decorator sets the success code:**
   `status.HTTP_201_CREATED` for `POST`, because something new now
   exists, and `status.HTTP_204_NO_CONTENT` for `DELETE`, because it's
   done and there's nothing to send back. Both also show up correctly in
   `/docs`.

8. **`responses={404: {...}}` is documentation only.** It doesn't change
   behaviour. It tells `/docs`, and anyone generating a client from the
   OpenAPI schema, that this route can also answer `404`.

From here on, every topic in this repo returns ORM rows with a
`response_model` instead of building dicts by hand.
