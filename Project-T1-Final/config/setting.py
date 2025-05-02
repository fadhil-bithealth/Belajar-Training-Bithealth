from pydantic_settings import BaseSettings, SettingsConfigDict

# class Settings(BaseSettings):
#     app_env: str
#     app_name: str
#     app_version: str
#     google_api_key: str

#     model_config = SettingsConfigDict(env_file=".env")
#     def __getitem__(self, item):
#         return getattr(self, item)
from dotenv import load_dotenv
import os

load_dotenv()
env = os.getenv 

# env = Settings()

class Settings(BaseSettings):
    google_api_key: str
    google_api_key2: str | None = None
    langsmith_tracing: str | None = None
    langsmith_endpoint: str | None = None
    langsmith_api_key: str | None = None
    langsmith_project: str | None = None

    class Config:
        env_file = ".env"
