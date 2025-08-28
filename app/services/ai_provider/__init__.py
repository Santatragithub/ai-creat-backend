from app.config import get_settings
from app.services.ai_provider.base import AIProviderBase
from app.services.ai_provider.openai_provider import OpenAIProvider
from app.services.ai_provider.gemini_provider import GeminiProvider
from app.services.ai_provider.mock_provider import MockProvider

settings = get_settings()


def get_ai_provider() -> AIProviderBase:
    provider = settings.AI_PROVIDER.lower()
    if provider == "openai":
        return OpenAIProvider()
    elif provider == "gemini":
        return GeminiProvider()
    elif provider == "mock":
        return MockProvider()
    else:
        raise ValueError(f"Unsupported AI provider: {settings.AI_PROVIDER}")
