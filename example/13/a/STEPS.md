# 13/a — Alembic instead of `create_all`, step by step

Same `database.py` as [6/a](../../6/a/STEPS.md), and the same
`response_model` style as [8/d](../../8/d). What's new is who creates
the table.

1. **Why not `create_all` anymore?** Every earlier `main.py` started
   with:

   ```python
   Base.metadata.create_all(bind=engine)
   ```

   It issues `CREATE TABLE` for each table that **doesn't exist yet**,
   and skips the rest. It never compares columns. So the day you add
   `description` to the model, `create_all` sees `migrated_items`
   already exists and does nothing, and the first query that selects
   `description` crashes. The only `create_all` fix is "drop the table
   and lose the data". Migrations instead record each change as a file
   that is:
   - **versioned**: the database stores which ones it has run, so each
     runs exactly once, in order, on every machine;
   - **reviewable**: it's code in git, read in a pull request like
     anything else;
   - **reversible**: each has a `downgrade()` that undoes it.

2. **`main.py` — no `create_all`, no seeding:**

   ```python
   # No Base.metadata.create_all() here, and no seeding. The table is created
   # (and later changed) by Alembic: run `alembic upgrade head` before
   # starting the app.
   ```

   The app now **assumes** the schema is right. Getting it right is a
   separate step (`alembic upgrade head`) that you run before starting
   the app, and in a real deployment before each new version goes live.

3. **`models.py` — the target, not the creator.** The model describes
   what the table should look like **after all migrations**:

   ```python
   class ItemModel(Base):
       __tablename__ = "migrated_items"

       id = Column(Integer, primary_key=True, autoincrement=True)
       name = Column(String(100), nullable=False)
       price = Column(Float, nullable=False)
       # Added later by migration 0002_add_description.
       description = Column(Text, nullable=True)
   ```

   The app uses it for queries, and autogenerate (step 10) compares it
   to the real database to find what's changed.

4. **`alembic init migrations` — where the files came from.** Run once,
   it generated `alembic.ini`, `migrations/env.py`,
   `migrations/script.py.mako` and an empty `migrations/versions/`.
   `script.py.mako` is left exactly as generated: it's the template for
   every new migration file. The other two were edited.

5. **`alembic.ini` — no URL in it.** The generated file has a
   placeholder `sqlalchemy.url = driver://user:pass@localhost/dbname`.
   It's commented out instead of filled in:

   ```ini
   # sqlalchemy.url = driver://user:pass@localhost/dbname
   ```

   A URL here would be a second copy of the connection details (which
   could drift from the app's), and the password would end up in git.
   The other important line was already there: `prepend_sys_path = .`
   puts the current folder on `sys.path`, which is what lets `env.py`
   import `database` and `models` in the next step.

6. **`env.py` — use the app's database and the app's models:**

   ```python
   import models  # noqa: F401
   from database import DATABASE_URL, Base
   ```

   ```python
   config.set_main_option("sqlalchemy.url", DATABASE_URL.replace("%", "%%"))

   # What autogenerate compares the real database against.
   target_metadata = Base.metadata
   ```

   `DATABASE_URL` is built in `database.py` from the same env vars and
   `.env` as the app, so `alembic upgrade head` always migrates the
   database the app will use. `import models` looks unused, but
   importing it is what registers `migrated_items` on `Base.metadata`.
   Without it, `target_metadata` would be empty. The `%` → `%%` is
   because `alembic.ini`-style config treats `%` as special, and a
   URL-encoded password (`p%40ss`) contains one.

7. **`env.py` — only look at our own tables.** This is the most
   important edit in this lesson:

   ```python
   def include_name(name, type_, parent_names):
       if type_ == "table":
           return name in target_metadata.tables
       return True
   ```

   `fastapi_learn` is shared by every topic. When autogenerate inspects
   it, it finds `items`, `crud_react_items`, `validation_items`, ... A
   table that's in the database but not in the models looks **removed**,
   so autogenerate would write `op.drop_table("items")` for each one.
   Run that migration and you've deleted other topics' data. The filter
   is called for every name Alembic finds in the database. Returning
   `False` for a table makes Alembic act as if it doesn't exist.

   (Tested: with the filter removed and an `items` table present,
   `alembic check` reports `Detected removed table 'items'`. With it,
   `No new upgrade operations detected`.)

8. **`env.py` — our own version table, and batch mode on SQLite:**

   ```python
   VERSION_TABLE = "alembic_version_13a"
   ```

   ```python
       context.configure(
           connection=connection,
           target_metadata=target_metadata,
           version_table=VERSION_TABLE,
           include_name=include_name,
           # SQLite can't ALTER most things in place. Batch mode makes
           # Alembic copy the table, change it, and swap it in instead.
           # MySQL doesn't need it, so it's only switched on for SQLite.
           render_as_batch=connection.dialect.name == "sqlite",
       )
   ```

   Alembic keeps one row in a version table holding the id of the last
   migration it ran. That row is how `upgrade head` knows to skip what's
   already done. The default name is `alembic_version`; a lesson-specific
   name means another project's Alembic in the same database can never
   overwrite ours. `render_as_batch` makes autogenerate wrap column
   changes in `batch_alter_table` (step 10), which SQLite needs. The
   same settings are passed in `run_migrations_offline()` too.

9. **The two migrations — a chain linked by ids.** Each file has a
   `revision` (its own id) and a `down_revision` (the one it comes
   after):

   ```python
   revision: str = "0001"
   down_revision: Union[str, Sequence[str], None] = None  # first migration
   ```

   ```python
   revision: str = "0002"
   down_revision: Union[str, Sequence[str], None] = "0001"  # runs after 0001
   ```

   That chain is what `alembic history` prints and the order
   `upgrade head` follows. Alembic normally makes random ids like
   `5d51e5d3eede`; these two were given readable ones.

   `0001` creates the table **as it was on day one**, without
   `description`, and seeds it:

   ```python
   items = op.create_table(
       "migrated_items",
       sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
       sa.Column("name", sa.String(length=100), nullable=False),
       sa.Column("price", sa.Float(), nullable=False),
       sa.PrimaryKeyConstraint("id"),
   )
   op.bulk_insert(
       items,
       [
           {"name": "Laptop", "price": 999.99},
           {"name": "Mouse", "price": 19.99},
       ],
   )
   ```

   Seeding moved here from `main.py`. The old "insert if the table is
   empty" check ran on every startup; this runs exactly once, right
   after the table is created, and `downgrade()` (`op.drop_table`)
   takes it away again. Note the migration uses plain `sa.Column`s, not
   `ItemModel`: a migration must describe the table as it was **at that
   point in history**, and `ItemModel` will keep changing.

   `0002` adds the column:

   ```python
   def upgrade() -> None:
       with op.batch_alter_table("migrated_items") as batch_op:
           batch_op.add_column(sa.Column("description", sa.Text(), nullable=True))


   def downgrade() -> None:
       with op.batch_alter_table("migrated_items") as batch_op:
           batch_op.drop_column("description")
   ```

   `nullable=True` is what makes this safe on a table that already has
   rows: they just get `NULL`. `downgrade()` is the exact reverse. On
   MySQL, `batch_alter_table` simply runs `ALTER TABLE`. On SQLite, it
   rebuilds the table, since SQLite can't drop a column in place.

10. **`--autogenerate` — Alembic writes the next one.** After you add
    `stock` to the model, `alembic revision --autogenerate -m "add
    stock"` connects to the database, compares it with
    `target_metadata`, and writes:

    ```python
    def upgrade() -> None:
        """Upgrade schema."""
        # ### commands auto generated by Alembic - please adjust! ###
        with op.batch_alter_table('migrated_items', schema=None) as batch_op:
            batch_op.add_column(sa.Column('stock', sa.Integer(), server_default='0', nullable=False))

        # ### end Alembic commands ###
    ```

    with `down_revision = '0002'` filled in for you. "please adjust!" is
    meant literally: it's a draft. Autogenerate sees two snapshots, not
    your intent, so a rename shows up as drop + add (data lost), and
    some changes, like a new `server_default` on an existing column,
    aren't detected at all. Read it, fix it, then `upgrade`.

11. **Migrations are append-only once shared.** The version table only
    remembers **ids**, not file contents. Change `0002` after a teammate
    has run it and their database will never see your change. The fix
    is always a new migration on top, never an edited old one.
