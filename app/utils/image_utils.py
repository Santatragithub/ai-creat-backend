from typing import Dict
from PIL import Image


def get_image_dimensions(file_path: str) -> Dict[str, int]:
    with Image.open(file_path) as img:
        return {"width": img.width, "height": img.height}


def resize_image(file_path: str, target_path: str, width: int, height: int) -> None:
    with Image.open(file_path) as img:
        resized = img.resize((width, height))
        resized.save(target_path)
