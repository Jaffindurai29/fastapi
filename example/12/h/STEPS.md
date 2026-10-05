# 12/h — Public ids with sqids, step by step

Same `database.py` as [6/a](../../6/a/STEPS.md), and the items routes
from [8/d](../../8/d). The only change is what an id looks like outside
the server.

1. **What's wrong with `/items/1`?** Sequential ids leak information:

   - **Counting.** Sign up, create an item, get id `5231`: the site has
     about 5,000 items. Do it again next month and you know its growth
     rate. Competitors love this.
   - **Enumeration.** If `/items/41` exists, so do `40` and `42`. A
     loop from 1 to 100,000 scrapes everything.

   Sqids turns each integer into a short string that *looks* random:
   1 → `igPHZLIU`, 2 → `uclL2dH9`. The database keeps its fast integer
   primary key. Only the API's view changes.

2. **`config.py` — the alphabet works like a salt.**

   ```python
   SQIDS_ALPHABET = os.getenv(
       "SQIDS_ALPHABET", "DpNyH4T2PcXBCbfRnV8s6qg7kwrhAOGLKQ0Uaot1ix9zvSjZMEuldWeFIYJm35"
   )
   # Pad short ids so id 1 isn't a tell-tale 1-2 character string.
   SQIDS_MIN_LENGTH = 8
   ```

   With sqids' default alphabet, anyone could decode your ids with one
   line of Python. A shuffled alphabet makes the mapping yours. But it's
   only obscurity, not a real secret (see step 6). Pick it **once**:
   changing it changes every public id, and every bookmarked or shared
   link breaks. `min_length=8` pads small numbers, so the first rows
   don't stand out with 2-character ids.

3. **`ids.py` — `encode_id`.**

   ```python
   sqids = Sqids(alphabet=SQIDS_ALPHABET, min_length=SQIDS_MIN_LENGTH)


   def encode_id(n: int) -> str:
       """Database id (int) -> public id (str), e.g. 1 -> 'igPHZLIU'."""
       return sqids.encode([n])
   ```

   Sqids encodes a *list* of numbers into one string. We always pass one.
   Nothing is stored: the public id is recomputed every time, so
   existing rows get one for free.

4. **`ids.py` — `decode_id` rejects anything we didn't hand out.**

   ```python
   def decode_id(public_id: str) -> int | None:
       """Public id -> database id, or None if it isn't one we'd ever hand out."""
       numbers = sqids.decode(public_id)  # [] for characters not in the alphabet
       if len(numbers) != 1:  # garbage, or several numbers packed into one id
           return None
       # sqids can decode several different strings to the same number. Only
       # accept the one string encode_id would produce, so every row has
       # exactly ONE valid public id.
       if encode_id(numbers[0]) != public_id:
           return None
       return numbers[0]
   ```

   The re-encode check matters. With the default alphabet, `igPHZLIU`,
   `igPHZLI` and even `ig` **all** decode to `1`. Without the check, one
   row would have many valid URLs: caches and "have I seen this id?"
   logic get confused, and it gives an attacker a way to probe the
   encoding. Encoding the number back and comparing keeps exactly one
   canonical id per row.

5. **`schemas.py` — `ItemOut.id` is a `str`.**

   ```python
   class ItemOut(BaseModel):
       id: str  # the PUBLIC id, never the database integer
       name: str
       price: float

       @classmethod
       def from_row(cls, row: ItemModel) -> "ItemOut":
           return cls(id=encode_id(row.id), name=row.name, price=row.price)
   ```

   [8/d](../../8/d) returned rows directly with `from_attributes=True`.
   That would copy `row.id` (an int) into `id: str` and fail. Other
   options exist (a `@field_serializer("id")` that encodes on output, or
   a `@computed_field`), but they hide the conversion inside Pydantic.
   One explicit `from_row` keeps it obvious: **every** response goes
   through it, so the integer can never leak by accident. The routes call
   it: `return ItemOut.from_row(row)`.

6. **`main.py` — decode at the edge, 404 for everything bad.**

   ```python
   def get_item_or_404(db: Session, public_id: str) -> ItemModel:
       item_id = decode_id(public_id)
       row = crud.get_item(db, item_id) if item_id is not None else None
       if row is None:
           raise HTTPException(status_code=404, detail="Item not found")
       return row
   ```

   The path parameter is `public_id: str`, not `int`, so `/items/1` is
   no longer a `422`. It's just a string that isn't a valid public id,
   so `404`. An invalid id and a valid-but-deleted one get the **same**
   `404`: the client learns nothing from the difference. `crud.py` never
   sees a public id. Converting happens only in the routes.

7. **What sqids is NOT.**

   - **Not encryption.** The ids are reversible by design, and anyone
     who learns your alphabet (it's in your code and your `.env`) can
     decode them. Don't put secrets in them, and don't rely on them being
     unguessable.
   - **Not access control.** If Alice can see Bob's note just by knowing
     its id, hiding the id only slows her down. You still need the
     ownership check from [12/f](../f/STEPS.md) on every route.
     Public ids reduce what leaks. They don't decide who's allowed.

8. **Alternatives.**

   | | Pros | Cons |
   |---|---|---|
   | **Sqids** (this lesson) | Short, URL-friendly, no extra column, integer PK stays | Obscurity only, alphabet must never change |
   | **UUID4** column (`uuid.uuid4()`) | Truly random, nothing to keep secret | 36 chars, a second indexed column (or a bigger, slower PK) |
   | **UUID7** | Random **and** time-ordered, indexes nicely | Reveals creation time, still long |
   | Random token column (`secrets.token_urlsafe(8)`) | Short and truly random | Must store it and handle (rare) collisions |

   Use a UUID when ids must be unguessable on their own (e.g. "anyone
   with the link can view"). Use sqids when you just don't want to
   advertise row counts and sequences.
