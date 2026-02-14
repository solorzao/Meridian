from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    app_name: str = "Meridian Analytics"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://meridian:meridian@localhost:5432/meridian"

    # Market data
    polygon_api_key: str | None = None

    # Cache settings (for future Redis integration)
    cache_ttl_quotes: int = 60  # 1 minute for premium
    cache_ttl_quotes_free: int = 900  # 15 minutes for free tier

    # Stripe
    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    stripe_premium_price_id: str | None = None

    # Azure OpenAI
    azure_openai_endpoint: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_deployment: str = "gpt-4o"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
