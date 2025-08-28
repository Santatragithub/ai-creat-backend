from typing import Dict


def check_file_type(filename: str, allowed_types: list[str]) -> bool:
    ext = filename.split(".")[-1].lower()
    return ext in allowed_types


def check_file_size(size_bytes: int, max_size_mb: int) -> bool:
    return size_bytes <= max_size_mb * 1024 * 1024


def nsfw_check_stub(file_path: str) -> Dict[str, bool]:
    # Stub for NSFW check (always returns safe).
    return {"is_nsfw": False}
