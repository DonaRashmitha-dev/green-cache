"""Application configuration using pydantic-settings."""

import os
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_provider: Literal["ollama", "groq", "openai", "deepseek"] = Field(default="ollama")
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="qwen2.5:0.5b")
    groq_api_key: str = Field(default="")
    groq_model: str = Field(default="qwen-2.5-32b")
    deepseek_api_key: str = Field(default="")
    deepseek_model: str = Field(default="deepseek-chat")
    openai_api_key: str = Field(default="")
    openai_base_url: str = Field(default="https://api.openai.com/v1")
    openai_model: str = Field(default="gpt-3.5-turbo")
    llm_max_tokens: int = Field(default=1024)
    llm_temperature: float = Field(default=0.0)
    cache_backend: Literal["memory", "redis", "lsh"] = Field(default="memory")
    redis_url: str = Field(default="redis://localhost:6379/0")
    redis_ttl_seconds: int = Field(default=3600)
    similarity_threshold: float = Field(default=0.92)
    embedding_model: str = Field(default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    lsh_num_perm: int = Field(default=128)
    lsh_threshold: float = Field(default=0.85)
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    log_level: str = Field(default="INFO")
    energy_per_token_wh: float = Field(default=0.0005)
    wue_l_per_kwh: float = Field(default=1.8)
    pue: float = Field(default=1.5)

    @property
    def is_production(self) -> bool:
        return os.getenv("ENV", "development").lower() == "production"


settings = Settings()
