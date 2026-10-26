from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.database import Base, engine
from backend.app.routers import (
    admissions,
    audit,
    auth,
    dashboard,
    findings,
    institutions,
    intake,
    programmes,
    reports,
    students,
    uploads,
    verification,
)

# Auto-create tables on startup (and Alembic for formal migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="SIH26263 APAAR Student Data Management & Verification Platform Backend API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include /api/v1 routers
api_prefix = settings.API_V1_STR
app.include_router(auth.router, prefix=api_prefix)
app.include_router(students.router, prefix=api_prefix)
app.include_router(admissions.router, prefix=api_prefix)
app.include_router(programmes.router, prefix=api_prefix)
app.include_router(institutions.router, prefix=api_prefix)
app.include_router(intake.router, prefix=api_prefix)
app.include_router(findings.router, prefix=api_prefix)
app.include_router(uploads.router, prefix=api_prefix)
app.include_router(verification.router, prefix=api_prefix)
app.include_router(dashboard.router, prefix=api_prefix)
app.include_router(reports.router, prefix=api_prefix)
app.include_router(audit.router, prefix=api_prefix)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENV,
    }


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "SIH26263 APAAR Platform API is operational.",
        "docs": f"{settings.API_V1_STR}/docs",
    }
