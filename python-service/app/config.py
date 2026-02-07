from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    app_name: str = "Meridian Analytics"
    debug: bool = False

    # Market data
    polygon_api_key: str | None = None

    # Cache settings (for future Redis integration)
    cache_ttl_quotes: int = 60  # 1 minute for premium
    cache_ttl_quotes_free: int = 900  # 15 minutes for free tier

    class Config:
        env_file = ".env"


settings = Settings()
