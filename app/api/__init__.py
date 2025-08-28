from app.api.routers import (
    auth,
    projects,
    generation,
    formats,
    admin_formats,
    admin_rules,
    admin_styles,
)

auth_router = auth.router
projects_router = projects.router
generation_router = generation.router
formats_router = formats.router
admin_formats_router = admin_formats.router
admin_rules_router = admin_rules.router
admin_styles_router = admin_styles.router
