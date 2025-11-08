from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Basic configuration for Flask app.
    """

    # App configuration
    name: str

    # Database configuration
    db_uri: str

    # Server configuration
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 5000

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
