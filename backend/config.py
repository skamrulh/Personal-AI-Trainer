import os

class Config:
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
    SESSION_FRAME_CAP = int(os.getenv("SESSION_FRAME_CAP", "120"))

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # LLM / caching
    LLM_CACHE_TTL = int(os.getenv("LLM_CACHE_TTL", "30"))  # seconds
    LLM_RATE_LIMIT_PER_MIN = int(os.getenv("LLM_RATE_LIMIT_PER_MIN", "6"))

    # App
    PORT = int(os.getenv("PORT", "5000"))
