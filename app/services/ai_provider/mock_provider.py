from typing import Any, Dict
from app.services.ai_provider.base import AIProviderBase


class MockProvider(AIProviderBase):
    def analyze_image(self, file_path: str) -> Dict[str, Any]:
        return {
            "detectedElements": ["mock-element"],
            "width": 640,
            "height": 480,
            "dpi": 72,
        }

    def generate_asset(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "url": "http://localhost/generated/mock_asset.png",
            "formatName": "Mock-format",
            "isNsfw": False,
        }
