# 1/a — Hello, FastAPI!, step by step

1. **Import the `FastAPI` class**: `from fastapi import FastAPI`.

2. **Create an app instance**: `app = FastAPI()`. This one object is
   what Uvicorn actually runs, and what you attach every route to.

3. **Write a decorator + function pair:**

   ```python
   @app.get("/")
   def read_root():
       return {"message": "Hello, FastAPI!"}
   ```

   `@app.get("/")` means "when a `GET` request comes in for `/`, run the
   function right below it." This pairing is called a **path
   operation**.

4. **Run it:** `uvicorn main:app --reload` — `main` is the file
   (`main.py`), `app` is the variable we created in step 2.

5. **Visit `http://127.0.0.1:8000/`** — you should see the JSON your
   function returned. Whatever a path operation function `return`s
   becomes the response.
