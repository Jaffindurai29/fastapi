from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


# Every setting the app reads, in one place, with a type and a default.
# Each field is filled from (highest priority first):
#   1. a real environment variable with the same name (any case:
#      APP_NAME, app_name, App_Name all fill app_name)
#   2. the .env file in the current folder
#   3. the default written here
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
    # SecretStr prints as '**********' in logs, tracebacks and repr().
    # Call .get_secret_value() at the one place that needs the real value.
    mysql_password: SecretStr = SecretStr("")
    mysql_db: str = "fastapi_learn"

    # Set to override every mysql_* field above at once.
    database_url: str | None = None

    api_key: SecretStr = SecretStr("dev-api-key")

    # Lists come from the environment as JSON:
    #   CORS_ORIGINS=["http://localhost:5173","https://example.com"]
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        password = self.mysql_password.get_secret_value()
        return (
            f"mysql+pymysql://{self.mysql_user}:{password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
        )


# Reading the environment and .env, then validating, happens once: the
# first call builds Settings(); every later call returns that same object.
@lru_cache
def get_settings() -> Settings:
    return Settings()
