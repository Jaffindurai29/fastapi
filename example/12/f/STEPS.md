# 12/f — Authorization by ownership, step by step

Login is the same as [12/b](../b/STEPS.md), `get_current_user` is the
same as [12/c](../c/STEPS.md), and the users table and the `role` column
are the ones from [12/e](../e/STEPS.md). [12/e](../e/STEPS.md) asked
"is this user an admin?". This lesson asks a different question: "is
this **row** yours?".

1. **The bug this lesson prevents: IDOR.** *Insecure Direct Object
   Reference*: the API checks that you're logged in, then happily returns
   `/notes/3` to whoever asks, because the route never compared the
   note's owner with the caller. Alice changes `1` to `3` in the URL and
   reads Bob's notes. Login, hashing and JWTs are all perfect, and the
   data still leaks. It's one of the most common security bugs in real
   APIs (it sits under "Broken Object Level Authorization", #1 on the
   OWASP API Top 10), precisely because it's not a missing feature, it's
   a missing `WHERE`.

2. **`models.py` — every note has an owner.**

   ```python
   owner_id = Column(
       Integer, ForeignKey("sec_rbac_users.id", ondelete="CASCADE"), nullable=False, index=True
   )
   ```

   `index=True` because "notes WHERE owner_id = ?" is now the most
   frequent query. `ondelete="CASCADE"` matters because [12/e](../e)
   shares the users table: when its admin deletes Bob, MySQL removes
   Bob's notes too, instead of refusing the delete with a foreign-key
   error. `UserModel` is copied unchanged from 12/e. Two folders can only
   share a table if their models are identical, because `create_all`
   never alters an existing table.

3. **`POST /notes` — the owner comes from the token, never the body.**

   ```python
   return crud.create_note(db, note, owner_id=user.id)
   ```

   `NoteIn` has no `owner_id` field at all. Even if a client sends
   `"owner_id": 999`, Pydantic ignores it. Letting the client pick the
   owner would let anyone create notes "as" someone else.

4. **`GET /notes` — filter in the query.**

   ```python
   def get_notes_for_owner(db: Session, owner_id: int) -> list[NoteModel]:
       return (
           db.query(NoteModel)
           .filter(NoteModel.owner_id == owner_id)
           .order_by(NoteModel.id)
           .all()
       )
   ```

   Don't load every note and drop the wrong ones in Python. Let the
   database return only the caller's rows. The route picks
   `get_all_notes` for an admin and `get_notes_for_owner` for everyone
   else. **Rule of thumb: every query that touches user-owned data
   should mention `owner_id`** (or go through a helper that does).

5. **`dependencies.py` — `get_note_for_user` does the check once.**

   ```python
   def get_note_for_user(
       note_id: int,
       user: UserModel = Depends(get_current_user),
       db: Session = Depends(get_db),
   ) -> NoteModel:
       note = crud.get_note(db, note_id)
       if note is None:
           raise HTTPException(status_code=404, detail="Note not found")
       if note.owner_id != user.id and user.role != "admin":
           raise HTTPException(
               status_code=status.HTTP_403_FORBIDDEN,
               detail="Not enough permissions",
           )
       return note
   ```

   `note_id` has no `Depends`, so FastAPI fills it from the path
   `/notes/{note_id}`, exactly as it would in a route. The order is
   always: no/bad token `401` (inside `get_current_user`), missing `404`,
   not yours `403`.

6. **`main.py` — routes receive a note that is already checked.**

   ```python
   @app.put("/notes/{note_id}", response_model=NoteOut, responses=NOTE_ERRORS)
   def replace_note(
       body: NoteIn,
       note: NoteModel = Depends(get_note_for_user),
       db: Session = Depends(get_db),
   ):
       return crud.update_note(db, note, body)
   ```

   `GET`, `PUT` and `DELETE` all use the same dependency, so there's one
   place to get the rule right instead of three places to forget it. A
   new `/notes/{note_id}/share` route would get the check by adding one
   parameter. FastAPI also caches dependencies per request:
   `get_db` here and inside `get_note_for_user` is the **same** session,
   so the note we change is attached to the session we commit.

7. **`403` or `404` for someone else's note?** `403` tells Alice "note 3
   exists, you just can't see it". That's a small leak: by trying ids she
   learns how many notes there are. Some APIs answer `404` instead, as if
   the row didn't exist. GitHub does this: a private repo you can't see
   is a `404 Not Found`, not a `403`. To do the same here, change the
   second `raise` to a `404` with the same message as the first.

   This lesson keeps `403` because it's clearer while learning and
   debugging ("you're logged in as the wrong user" vs "wrong id"). Pick
   `404` when the mere existence of a row is sensitive. [12/h](../h)
   attacks the same leak from another side by making ids unguessable,
   but that never replaces this ownership check.
