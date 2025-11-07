from functools import lru_cache
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)


class Settings:
    """Basic configuration values loaded from environment variables."""

    def __init__(self) -> None:
        self.environment = os.getenv("APP_ENV", "local")
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg2://myuser:mypassword@localhost:5433/mydb",
        )
        self.secret_key = os.getenv("SECRET_KEY", "change-me")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    def model_dump(self) -> dict[str, Any]:
        return {
            "environment": self.environment,
            "database_url": self.database_url,
            "jwt_algorithm": self.jwt_algorithm,
            "access_token_expire_minutes": self.access_token_expire_minutes,
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

