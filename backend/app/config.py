import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model = os.getenv("LLM_MODEL", os.getenv("GEMINI_MODEL", "gemini-2.5-flash")).strip()
        if self.gemini_api_key and not os.getenv("GOOGLE_API_KEY"):
            os.environ["GOOGLE_API_KEY"] = self.gemini_api_key

    @property
    def has_key(self):
        return bool(self.gemini_api_key)

    @property
    def llm_enabled(self):
        if self.provider == "ollama":
            return True
        return bool(self.gemini_api_key)


@lru_cache
def get_settings():
    return Settings()
