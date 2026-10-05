from typing import Literal

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Only ever used in development. Production refuses to start with it.
DEV_SECRET_KEY = "dev-only-secret-key-do-not-use-in-production"


class Settings(BaseSettings):
    # CHECKLIST: secrets come from the environment (or .env), never from
    # code. Each field is read from the env var of the same name,
    # case-insensitive: SECRET_KEY -> secret_key, DATABASE_URL -> database_url.
    # hide_input_in_errors: if validation fails, the error message must
    # not print the values it was given (one of them is the secret key).
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", hide_input_in_errors=True)

    environment: Literal["development", "production"] = "development"

    # SecretStr hides the value in repr()/logs: it prints as '**********'.
    # Call .get_secret_value() at the one place that really needs it.
    secret_key: SecretStr = SecretStr(DEV_SECRET_KEY)

    # CHECKLIST: short-lived access tokens. A stolen one is useful for
    # 15 minutes, not forever. The refresh token gets a new one.
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # CHECKLIST: CORS origins are an explicit list from settings.
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # CHECKLIST: rate-limited login (see routers/auth.py).
    login_rate_limit: str = "5/minute"

    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: SecretStr = SecretStr("")
    mysql_db: str = "fastapi_learn"
    # Set DATABASE_URL to override all the mysql_* fields at once.
    database_url: str | None = None

    @property
    def sqlalchemy_url(self) -> str:
        if self.database_url:
            return self.database_url
        password = self.mysql_password.get_secret_value()
        return (
            f"mysql+pymysql://{self.mysql_user}:{password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
        )

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    # CHECKLIST: fail fast. A production server with the well-known dev
    # key would let anyone forge tokens, so it must not start at all.
    @model_validator(mode="after")
    def check_production_secret(self) -> "Settings":
        if self.is_production:
            key = self.secret_key.get_secret_value()
            if key == DEV_SECRET_KEY:
                raise ValueError("SECRET_KEY must be set in production (the dev default is public)")
            if len(key) < 32:
                raise ValueError("SECRET_KEY must be at least 32 characters in production")
        return self


settings = Settings()
