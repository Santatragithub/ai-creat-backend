from typing import Any, Dict
from app.services.ai_provider.base import AIProviderBase


class GeminiProvider(AIProviderBase):
    def analyze_image(self, file_path: str) -> Dict[str, Any]:
        return {"detectedElements": ["product"], "width": 1024, "height": 768}

    def generate_asset(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"url": "http://localhost/generated/gemini_asset.png", "formatName": "Gemini-format"}
