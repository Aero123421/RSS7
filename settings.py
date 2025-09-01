from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Load configuration from environment variables."""

    DISCORD_TOKEN: str
    CLIENT_ID: str
    GUILD_ID: str
    GOOGLE_API_KEY: Optional[str] = None
    API_BASE_URL: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def load_settings() -> "Settings":
    """Return validated settings or raise a helpful error."""

    try:
        return Settings()
    except ValidationError as exc:  # pragma: no cover - exercised in tests
        missing = ", ".join(err["loc"][0] for err in exc.errors())
        raise RuntimeError(
            "Missing required environment variables: "
            f"{missing}. Please see README.md for setup instructions."
        ) from exc
