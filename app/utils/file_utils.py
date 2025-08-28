import os
import shutil
from uuid import UUID

UPLOAD_DIR = "/data/uploads"
GENERATED_DIR = "/data/generated"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)


def save_upload_file(file_obj, filename: str) -> str:
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file_obj, buffer)
    return file_path


def get_generated_file_path(asset_id: UUID, format_id: UUID) -> str:
    return os.path.join(GENERATED_DIR, f"{asset_id}_{format_id}.png")
