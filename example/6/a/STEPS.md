# 6/a — GET (MySQL), step by step

The code is split across `database.py`, `models.py`, `crud.py`, and
`main.py` instead of one file — see [README.md](README.md#files) for
what each one is responsible for.

1. **`database.py` — connection settings from environment variables**,
   with a `DATABASE_URL` escape hatch to override everything at once
   (used for testing against SQLite instead of a real MySQL server).
   `load_dotenv()` runs first, so a local `.env` (copied from
   `.env.example`) is picked up automatically if you created one:

   ```python
   load_dotenv()

   DATABASE_URL = os.getenv(
       "DATABASE_URL",
       f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}",
   )
   ```

2. **`models.py` — the table, as a Python class:**

   ```python
   class ItemModel(Base):
       __tablename__ = "items"
       id = Column(Integer, primary_key=True, autoincrement=True)
       value = Column(String(255), nullable=False)
   ```

   `id` is a real, stable, auto-incrementing primary key — unlike the
   array topic, deleting a row never shifts anyone else's `id`. This
   `items` table is shared by every letter in this topic (`6/a`
   through `6/e`) — they all point at the same table, so data one
   folder writes is visible from another if you run them against the
   same database.

3. **`main.py` — `Base.metadata.create_all(bind=engine)`** — creates the
   table if it doesn't already exist. Safe to run every time the app
   starts.

4. **`main.py` — seed two rows once, only if the table is empty** — so
   restarting the app doesn't keep adding duplicates. This lives in
   `crud.py` as `seed_items(db)`, called from `main.py` at startup:

   ```python
   # crud.py
   def seed_items(db: Session) -> None:
       if db.query(ItemModel).count() == 0:
           db.add_all([ItemModel(value="first"), ItemModel(value="second")])
           db.commit()
   ```

5. **`database.py` — `get_db()`, a dependency that opens one session per
   request**, and always closes it afterward, even if the route raises
   an error. This is the same dependency-injection pattern from earlier
   topics, applied to a real database session.

6. **`crud.py` — the actual database logic, kept HTTP-agnostic:**
   `get_items(db)` queries every row, ordered by `id`. `get_item(db,
   item_id)` uses `db.get(ItemModel, item_id)` — SQLAlchemy's shortcut
   for "fetch by primary key," returning `None` if nothing matches.
   Neither function raises an exception on a miss.

7. **`main.py` — the routes**, which call into `crud.py` and only
   handle the HTTP concerns: `GET /items` returns
   `crud.get_items(db)` reshaped into plain dicts; `GET
   /items/{item_id}` calls `crud.get_item(db, item_id)` and turns a
   `None` result into `HTTPException(status_code=404, ...)`.
