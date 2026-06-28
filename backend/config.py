from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    otari_base_url: str = "https://api.inference.mozilla.ai"
    otari_api_key: str = ""
    otari_timeout_seconds: float = 45.0
    smallest_ai_api_key: str = ""
    gemini_api_key: str = ""
    gemini_vision_model: str = "gemini-1.5-flash-latest"
    otari_small_model: str = "Qwen/Qwen3-32B"
    otari_medium_model: str = "Qwen/Qwen3-30B-A3B-Instruct-2507"
    otari_large_model: str = "Qwen/Qwen3-Next-80B-A3B-Thinking"
    otari_vision_model: str = "Qwen/Qwen2.5-VL-72B-Instruct"
    initial_budget_usd: float = 2.0
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
