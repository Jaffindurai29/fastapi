# 11/c — Many-to-many, step by step

Same `database.py` as [6/a](../../6/a/STEPS.md). `CategoryModel` is
copied unchanged from [11/a](../a/STEPS.md), and `ItemModel` keeps the
exact same columns.

1. **Why a third table?** In 11/a the link lived on the "many" side:
   each item had one `category_id`. With tags both sides are "many". An
   item can't store a list of tag ids in one column, and a tag can't
   store a list of item ids. So the link gets its own table, one row
   per pair:

   ```text
   rel_item_tags
   item_id | tag_id
   --------+-------
         1 |      1     Laptop has "sale"
         1 |      2     Laptop has "new"
         3 |      2     FastAPI Guide has "new"
   ```

2. **`models.py` — the association table:**

   ```python
   item_tags = Table(
       "rel_item_tags",
       Base.metadata,
       Column("item_id", ForeignKey("rel_items.id"), primary_key=True),
       Column("tag_id", ForeignKey("rel_tags.id"), primary_key=True),
   )
   ```

   A plain `Table`, not a model class, because it holds nothing but the
   two foreign keys and you never query it directly. Both columns
   together are the primary key (a **composite** key), so the same
   (item, tag) pair can't be stored twice. The column types are copied
   from the columns the foreign keys point at.

3. **`models.py` — `secondary=` on both sides:**

   ```python
   # on ItemModel
   tags = relationship(
       "TagModel", secondary=item_tags, back_populates="items", order_by="TagModel.id"
   )

   # on TagModel
   items = relationship(
       "ItemModel", secondary=item_tags, back_populates="tags", order_by="ItemModel.id"
   )
   ```

   `secondary=item_tags` says "to get from an item to its tags, go
   through this table". `item.tags` is a list of `TagModel`,
   `tag.items` a list of `ItemModel`. `order_by` keeps the lists in a
   stable order so responses don't shuffle.

4. **Is it safe to share `rel_items` with 11/a and 11/b?** Yes.
   `create_all` never changes an existing table, so sharing is only safe
   if every app's model produces the same table. `tags` is a
   `relationship()`, not a `Column`: it adds nothing to `rel_items`. The
   generated MySQL `CREATE TABLE rel_items` is byte-for-byte the same in
   11/a, 11/b and 11/c. Run 11/a first and then 11/c against the same
   database, and 11/c's `create_all` skips `rel_categories` and
   `rel_items` and only creates `rel_tags` and `rel_item_tags`.

   ```python
   # main.py
   Base.metadata.create_all(bind=engine)
   ```

5. **`crud.py` — the seed handles "items already exist":**

   ```python
   if db.query(TagModel).count() == 0:
       sale = TagModel(name="sale")
       new = TagModel(name="new")
       laptop = db.query(ItemModel).filter(ItemModel.name == "Laptop").first()
       ...
       if laptop is not None:
           laptop.tags.extend([sale, new])
   ```

   The categories and items may have been seeded by 11/a already, so
   tags are seeded on their own check. `laptop.tags.extend(...)` is the
   whole "insert into the join table" step: on commit SQLAlchemy writes
   one `rel_item_tags` row per tag.

6. **`routers/items.py` — validate every tag id in one query:**

   ```python
   wanted = set(item.tag_ids)  # set() also drops duplicates like [1, 1]
   tags = crud.get_tags_by_ids(db, list(wanted))
   missing = sorted(wanted - {tag.id for tag in tags})
   if missing:
       raise HTTPException(status_code=404, detail=f"Tag(s) not found: {missing}")
   return crud.create_item(db, item, tags)
   ```

   `get_tags_by_ids` is `WHERE id IN (...)`: one query, however many
   ids. Whatever we asked for but didn't get back doesn't exist, and the
   error lists all of them at once. All checks run **before** anything
   is written, so a bad id creates nothing.

7. **`crud.py` — `tag_ids` isn't a column:**

   ```python
   row = ItemModel(**item.model_dump(exclude={"tag_ids"}), tags=tags)
   ```

   `ItemModel(tag_ids=...)` would fail, so it's left out of the dump and
   the loaded `TagModel` objects go in through the relationship instead.
   One `commit` inserts the item, then the join-table rows.

8. **`PUT` to attach, and why it's idempotent:**

   ```python
   def attach_tag(db: Session, item: ItemModel, tag: TagModel) -> ItemModel:
       if tag not in item.tags:  # already attached -> nothing to do
           item.tags.append(tag)
           db.commit()
           db.refresh(item)
       return item
   ```

   The URL `/items/2/tags/3` names the exact link. "Make sure item 2 has
   tag 3" gives the same result no matter how many times you send it,
   which is what `PUT` promises (idempotent). Without the `if`,
   appending twice would try to insert the same pair again and the
   composite primary key would reject it with an `IntegrityError`.

9. **`DELETE` to detach:**

   ```python
   if tag not in item.tags:
       raise HTTPException(status_code=404, detail="Tag is not attached to this item")
   crud.detach_tag(db, item, tag)
   ```

   `item.tags.remove(tag)` deletes the `rel_item_tags` row only. The item
   and the tag both stay. `404` when the link isn't there: the resource
   at that URL (the link) doesn't exist. Some APIs answer `204` here too,
   treating `DELETE` as idempotent; either is defensible, just be
   consistent.

10. **`routers/tags.py` — the other direction for free:**

    ```python
    return tag.items
    ```

    Same join table, read from the tag's side. `ItemSummary` has no
    `tags` field, for the same reason 11/b's `ItemSummary` has no
    `category`: no circular nesting.
