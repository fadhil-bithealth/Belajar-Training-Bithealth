from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str
    app_name: str
    app_version: str
    google_api_key: str
    langsmith_tracing: str
    langsmith_endpoint: str
    langsmith_api_key: str
    langsmith_project: str

    model_config = SettingsConfigDict(env_file=".env")

    def __getitem__(self, item):
        return getattr(self, item)

env = Settings()
