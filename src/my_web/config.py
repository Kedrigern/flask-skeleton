from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Basic configuration for Flask app.
    """

    # App configuration
    name: str = "my_web"
    secret_key: str = "test_secret"  # Do not forget to change!

    # Database configuration
    sqlalchemy_database_uri: str = "sqlite:///project.db"

    # Server configuration
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 5000

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


try:
    settings = Settings()
except Exception as e:
    raise RuntimeError(f"Settings is missing: {e}")
