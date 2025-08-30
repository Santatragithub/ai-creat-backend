from app.api.routers.auth import router as auth_router
from app.api.routers.projects import router as projects_router
from app.api.routers.generation import router as generation_router
from app.api.routers.formats import router as formats_router
from app.api.routers.admin_formats import router as admin_formats_router
from app.api.routers.admin_rules import router as admin_rules_router
from app.api.routers.admin_styles import router as admin_styles_router

__all__ = [
    "auth_router",
    "projects_router",
    "generation_router",
    "formats_router",
    "admin_formats_router",
    "admin_rules_router",
    "admin_styles_router",
]
