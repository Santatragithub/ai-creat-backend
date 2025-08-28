from abc import ABC, abstractmethod
from typing import Any, Dict


class AIProviderBase(ABC):
    @abstractmethod
    def analyze_image(self, file_path: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def generate_asset(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
