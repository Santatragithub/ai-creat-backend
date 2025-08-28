from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api import routers

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routers.auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(routers.projects_router, prefix=settings.API_V1_PREFIX)
app.include_router(routers.generation_router, prefix=settings.API_V1_PREFIX)
app.include_router(routers.formats_router, prefix=settings.API_V1_PREFIX)
app.include_router(routers.admin_formats_router, prefix=settings.API_V1_PREFIX)
app.include_router(routers.admin_rules_router, prefix=settings.API_V1_PREFIX)
app.include_router(routers.admin_styles_router, prefix=settings.API_V1_PREFIX)
