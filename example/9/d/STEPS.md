# 9/d — Page envelope, step by step

Same `database.py` and `models.py` as [9/a](../a/STEPS.md), same
filters and sort as [9/b](../b/STEPS.md). What's new: page numbers
instead of offsets, a total count, and a response that's an object
instead of a bare list.

1. **Why a frontend needs `total`.** A bare list of 10 rows can't
   answer the questions a UI asks: "Is there a next page?", "How many
   page buttons do I draw?", "What do I put in '25 results'?". The only
   way to know with 9/a–9/c is to request the next page and see if it's
   empty. One extra number, the total, answers all three.

2. **`schemas.py` — the envelope.**

   ```python
   class ItemPage(BaseModel):
       items: list[ItemOut]
       total: int  # rows matching the filters, across ALL pages
       page: int
       size: int
       pages: int  # ceil(total / size)
   ```

   `items` is a list of the same `ItemOut` from [8/d](../../8/d), so
   each row still goes out through the same filter of allowed fields.
   Returning an object instead of a list also leaves room to add more
   keys later without breaking clients.

3. **`main.py` — `page` and `size` instead of `skip` and `limit`.**

   ```python
   page: int = Query(1, ge=1, description="Page number, starting at 1"),
   size: int = Query(10, ge=1, le=100, description="Rows per page (max 100)"),
   ```

   Same idea, friendlier units: people think "page 3", databases think
   "skip 20". Pages start at 1, so `ge=1` makes `?page=0` and
   `?page=-1` a `422`. `size` keeps 9/c's ceiling of 100.

4. **`crud.py` — page → offset.**

   ```python
   offset = (page - 1) * size
   ```

   | `page` | `size` | `offset` | Rows |
   |---|---|---|---|
   | 1 | 10 | 0 | 1–10 |
   | 2 | 10 | 10 | 11–20 |
   | 3 | 10 | 20 | 21–25 (only 5 left) |
   | 3 | 2 | 4 | 5–6 |

   The `- 1` is because page 1 skips nothing.

5. **`crud.py` — count with the same filters, before paging.**

   ```python
   # 2. Count it NOW: same filters, but before offset/limit. Counting
   #    db.query(ItemModel) instead would give 25 even when the filter
   #    only matches 5, and the page numbers would be wrong.
   total = query.count()
   ```

   `query` at this point already has every `WHERE` from step 1 of the
   function, but no `ORDER BY`, `OFFSET` or `LIMIT` yet. `.count()` runs
   `SELECT count(*) FROM (that query)` and returns a number. Two rules:

   - **Same filters.** `?category=toys` must give `total: 5`, not 25.
     If `total` counted the whole table, a UI would draw 3 pages of
     toys with `size=10` and pages 2 and 3 would be empty. Reusing the
     same `query` object makes it impossible for the two to drift
     apart.
   - **Before `offset`/`limit`.** Counting after `.limit(size)` would
     answer "how many on this page", which is at most `size`, and the
     client already knows that from `len(items)`.

   It's two queries per request (one count, one page). That's the
   normal price of a total.

6. **`crud.py` — then sort and cut the page.**

   ```python
   rows = query.order_by(column, ItemModel.id).offset(offset).limit(size).all()

   return rows, total
   ```

   The function returns both, as a tuple, so `main.py` can build the
   envelope.

7. **`main.py` — `pages` is a ceiling division.**

   ```python
   return {
       "items": rows,  # ORM rows; ItemPage turns each into an ItemOut
       "total": total,
       "page": page,
       "size": size,
       "pages": math.ceil(total / size),
   }
   ```

   25 rows at 10 per page is 2.5, and the half page still needs a page,
   so round **up**: 3. Exact fits stay exact (25 / 25 = 1), and 0 rows
   gives 0 pages.

8. **Out-of-range pages are not errors.** `?page=9` on 3 pages returns
   `200` with `"items": []`, the same choice as 9/a's `?skip=100`. Rows
   get deleted while people are reading; a client sitting on page 3
   when the data shrinks to 2 pages should get an empty page and the
   new `pages` value, not a crash. `page` is still checked for being
   `1` or more, because page 0 is never meaningful.
