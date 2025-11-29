import os

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    ORCHESTRATOR_MODEL: str = "gemini-2.0-flash-exp"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
