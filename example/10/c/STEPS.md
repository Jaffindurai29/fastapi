# 10/c — Settings, step by step

Starts from [10/b](../b/STEPS.md). `models.py`, `schemas.py`, `crud.py`
and both routers are unchanged. What changes is **where configuration
comes from**: `config.py` is new, and `database.py`,
`dependencies.py` and `main.py` all read from it.

1. **The problem with `os.getenv`.** Until now, settings were read like
   this, in whichever file needed them:

   ```python
   MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
   ```

   - Everything is a **string**. `os.getenv("DEBUG")` is `"false"`, and
     `"false"` is truthy in Python.
   - A typo (`MYSQL_PORT=33o6`) isn't noticed until the first database
     query fails, maybe minutes after startup.
   - To find out what the app can be configured with, you'd grep every
     file for `getenv`.

2. **`config.py` — one class lists every setting:**

   ```python
   class Settings(BaseSettings):
       model_config = SettingsConfigDict(
           env_file=".env",
           # .env may hold variables for other tools too; ignore them
           # instead of refusing to start.
           extra="ignore",
       )

       app_name: str = "Structured Items API"
       debug: bool = False  # DEBUG=true / 1 / yes / on -> True

       mysql_host: str = "127.0.0.1"
       mysql_port: int = 3306  # MYSQL_PORT=abc fails at startup, not at first query
       mysql_user: str = "root"
       ...
   ```

   `BaseSettings` (from the `pydantic-settings` package) is a Pydantic
   model that fills its fields from the environment instead of from a
   request body. Same types, same validation as the `ItemCreate`
   schemas you already know.

3. **How environment variables map to fields.** Each field is filled
   from, highest priority first:
   1. a real **environment variable** with the same name. Matching is
      case-insensitive: `MYSQL_HOST`, `mysql_host` and `Mysql_Host` all
      fill `mysql_host`.
   2. the **`.env` file** in the current folder (`env_file=".env"`).
      No `load_dotenv()` call needed any more.
   3. the **default** written in the class.

   So `.env` is for your machine's everyday values, and an environment
   variable still beats it for a one-off run. That's why
   `DATABASE_URL=sqlite:///./test.db uvicorn main:app` keeps working
   exactly as it did in topic 6.

4. **Type conversion happens for you:**

   | Environment | Field | Value in Python |
   |---|---|---|
   | `DEBUG=true` (or `1`, `yes`, `on`) | `debug: bool` | `True` |
   | `MYSQL_PORT=3307` | `mysql_port: int` | `3307` |
   | `MYSQL_PORT=abc` | `mysql_port: int` | **startup fails** with a `ValidationError` naming `mysql_port` |
   | `CORS_ORIGINS=["http://localhost:5173","https://shop.example"]` | `cors_origins: list[str]` | a real list |

   Lists (and dicts) are written as **JSON** in the environment, with
   double quotes around each string.

5. **`SecretStr` for passwords and keys:**

   ```python
   # SecretStr prints as '**********' in logs, tracebacks and repr().
   # Call .get_secret_value() at the one place that needs the real value.
   mysql_password: SecretStr = SecretStr("")
   ```

   ```python
   api_key: SecretStr = SecretStr("dev-api-key")
   ```

   If `settings` ever ends up in a log line or an error page, the
   password shows as `**********`. To actually use it you have to write
   `.get_secret_value()`, which makes every place that touches a secret
   easy to find.

6. **Building the database URL, with `DATABASE_URL` still on top:**

   ```python
   # Set to override every mysql_* field above at once.
   database_url: str | None = None
   ```

   ```python
   @property
   def sqlalchemy_database_url(self) -> str:
       if self.database_url:
           return self.database_url
       password = self.mysql_password.get_secret_value()
       return (
           f"mysql+pymysql://{self.mysql_user}:{password}"
           f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
       )
   ```

   Same rule as [6/a's `database.py`](../../6/a/STEPS.md): if
   `DATABASE_URL` is set, use it as-is; otherwise build a MySQL URL from
   the parts. A `@property` is computed when read, so it's never stale.

7. **`get_settings()` — read once, reuse everywhere:**

   ```python
   @lru_cache
   def get_settings() -> Settings:
       return Settings()
   ```

   `Settings()` reads the environment, parses `.env` and validates
   everything. `@lru_cache` remembers the result of the first call, so
   every later `get_settings()` returns the **same object** without
   re-reading anything. Changing `.env` therefore needs a restart
   (`--reload` does that for you when a `.py` file changes, not when
   `.env` does).

8. **`database.py` — three lines instead of fifteen:**

   ```python
   settings = get_settings()

   engine = create_engine(settings.sqlalchemy_database_url, pool_pre_ping=True)
   ```

9. **`dependencies.py` — settings as a dependency:**

   ```python
   def require_api_key(
       x_api_key: str | None = Header(default=None),
       settings: Settings = Depends(get_settings),
   ) -> None:
       expected = settings.api_key.get_secret_value()
   ```

   `get_settings` is an ordinary function, so `Depends(get_settings)`
   works like any other dependency from [10/b](../b/STEPS.md). Asking
   for it via `Depends` (instead of calling it at the top of the file)
   means a test can swap in different settings:

   ```python
   app.dependency_overrides[get_settings] = lambda: Settings(api_key="test-key")
   ```

10. **`main.py` — the app itself is configured from settings:**

    ```python
    settings = get_settings()

    # The title shows at the top of /docs. debug=True makes unhandled errors
    # return a traceback page instead of a bare "Internal Server Error".
    app = FastAPI(title=settings.app_name, debug=settings.debug)
    ```

    ```python
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        ...
    )
    ```

    CORS works exactly as in [7/a](../../7/a/STEPS.md); only the list of
    allowed origins moved out of the code. Keep `DEBUG=false` anywhere
    real: a traceback page tells an attacker a lot about your code.

11. **`GET /info` — show settings, never secrets:**

    ```python
    @app.get("/info", tags=["meta"])
    def info(settings: Settings = Depends(get_settings)):
        return {"app_name": settings.app_name, "debug": settings.debug}
    ```

    Handy for checking which configuration a running server actually
    picked up. It returns only harmless fields, picked one by one;
    never `return settings` from a route.

12. **Why this beats `os.getenv`, in short:**
    - **One place:** `config.py` is the full list of everything the app
      can be configured with, with defaults.
    - **Typed:** `settings.mysql_port` is an `int`, `settings.debug` is a
      real `bool`, and your editor autocompletes them.
    - **Validated at startup:** a bad value stops the app immediately
      with a clear error, instead of failing later on some request.
    - **Secrets are masked** with `SecretStr`.
    - **Testable:** override `get_settings` instead of patching
      `os.environ`.
