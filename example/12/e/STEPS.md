# 12/e — Authorization by role, step by step

Login (`POST /token`, password hashing, the JWT) works exactly as in
[12/b](../b/STEPS.md), and `get_current_user` is a slimmed-down copy of the one from
[12/c](../c/STEPS.md) (no `is_active` column, one generic `401`
message). This lesson adds one column and one dependency factory on top.

1. **Two different questions, two different status codes.**

   | | Question | Fails with |
   |---|---|---|
   | **Authentication** | *Who are you?* (valid token for a real user?) | `401 Unauthorized` + `WWW-Authenticate: Bearer` |
   | **Authorization** | *What may you do?* (is that user allowed here?) | `403 Forbidden` |

   The names are confusing (`401` is literally called "Unauthorized"
   but means "unauthenticated"), so remember it this way: `401` = "log
   in (again)", `403` = "logging in again won't help, you aren't allowed".

2. **`models.py` — a `role` column.** Two roles fit in a plain string;
   new users get `"user"` by default:

   ```python
   role = Column(String(20), nullable=False, default="user")
   ```

   The table is `sec_rbac_users`, and [12/f](../f) uses the identical
   model, so both lessons can share it.

3. **`dependencies.py` — `require_role(*roles)` builds a dependency.**

   ```python
   def require_role(*roles: str):
       def role_checker(user: UserModel = Depends(get_current_user)) -> UserModel:
           if user.role not in roles:
               raise HTTPException(
                   status_code=status.HTTP_403_FORBIDDEN,
                   detail="Not enough permissions",
               )
           return user

       return role_checker
   ```

   `Depends()` needs a function, but each route needs a *different*
   allowed list. So `require_role("admin")` is a function that
   **returns** a function: the inner `role_checker` remembers `roles`.
   It depends on `get_current_user`, so the order is always: no/bad
   token → `401` first, wrong role → `403` second, then your route.
   `require_role("user", "admin")` would allow either.

4. **`main.py` — guarding a route is one parameter.**

   ```python
   @app.get("/admin/users", response_model=list[UserOut])
   def list_users(
       admin: UserModel = Depends(require_role("admin")), db: Session = Depends(get_db)
   ):
       return crud.get_users(db)
   ```

   The body never runs for a non-admin. You also get the admin row back
   (`admin`), which `DELETE` uses. To guard a whole group of routes at
   once you could write `APIRouter(dependencies=[Depends(require_role("admin"))])`
   instead.

5. **Role in the token, but read from the database.** The token carries
   the role:

   ```python
   payload = {"sub": username, "role": role, "exp": expire, "type": "access"}
   ```

   ...but nothing on the server reads `payload["role"]`. `get_current_user`
   loads a fresh row on every request and `require_role` checks
   `user.role` from **that row**:

   ```python
   # A fresh row from the database on every request, so user.role is the
   # role RIGHT NOW, not the one written into the token at login time.
   user = crud.get_user_by_username(db, username)
   ```

   Why? A JWT can't be changed once issued. If the server trusted the
   role inside it, demoting someone (or deleting them) would do nothing
   until their token expired. Re-reading costs one small query and makes
   role changes take effect **immediately**. The role in the token is
   still handy for a frontend (show or hide an "Admin" button), but it's
   only a hint.

6. **`schemas.py` — `Literal` limits the allowed roles.**

   ```python
   class RoleUpdate(BaseModel):
       role: Literal["user", "admin"]
   ```

   `{"role": "superuser"}` is a `422` before the route runs, the same
   validation you saw in [8/a](../../8/a/STEPS.md). `UserOut` returns
   `id`, `username` and `role`, and never `hashed_password`.

7. **`DELETE` — don't let an admin delete themselves.**

   ```python
   if user_id == admin.id:
       raise HTTPException(status_code=400, detail="You cannot delete your own account")
   ```

   That's a business rule, not a permission, so it's `400`, not `403`.
   Note there is no such guard on `PATCH`: an admin *can* demote
   themselves. If they were the last admin, nobody could undo it. A
   real app would refuse to remove the last admin.
