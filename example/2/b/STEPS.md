# 2/b — Fixed path before dynamic path, step by step

1. **Declare the fixed path first:**

   ```python
   @app.get("/users/me")
   def read_current_user():
       return {"user_id": "the current user"}
   ```

2. **Declare the dynamic path second:**

   ```python
   @app.get("/users/{user_id}")
   def read_user(user_id: str):
       return {"user_id": user_id}
   ```

3. **Why order matters:** FastAPI checks routes top-to-bottom and uses
   the first match. If `/users/{user_id}` were declared *first*, a
   request to `/users/me` would match it instead, and `user_id` would
   end up being the literal text `"me"`.
