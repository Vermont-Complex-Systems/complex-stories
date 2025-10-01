from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .routers import open_academic_analytics, datasets
from .internal import admin

app = FastAPI(
    title=settings.app_name,
    description="Backend API for Complex Stories data platform",
    version=settings.version,
    debug=settings.debug,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(open_academic_analytics.router, prefix="/open-academic-analytics", tags=["academics"])
app.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])


@app.get("/")
async def root():
    return {"message": "Complex Stories API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}