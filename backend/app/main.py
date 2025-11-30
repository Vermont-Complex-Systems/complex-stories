from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from .core.config import settings
from .core.database import connect_to_database, close_database_connection
from .routers import open_academic_analytics, datasets, auth, wikimedia, annotations, scisciDB, datalakes
from .internal import admin

app = FastAPI(
    title=settings.app_name,
    description="Backend API for Complex Stories data platform",
    version=settings.version,
    debug=settings.debug,
)

# Database events
@app.on_event("startup")
async def startup_event():
    await connect_to_database()

    # Create tables if they don't exist
    from .core.database import database
    from .models import Base

    if database.engine:
        async with database.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Create admin user if it doesn't exist
        from .core.database import get_db_session
        from .models.auth import User
        from .core.auth import get_password_hash
        from sqlalchemy import select

        async for db in get_db_session():
            result = await db.execute(select(User).where(User.username == "admin"))
            if not result.scalar_one_or_none():
                admin = User(
                    username="admin",
                    email="admin@complexstories.uvm.edu",
                    password_hash=get_password_hash("admin123"),
                    role="admin",
                    is_active=True
                )
                db.add(admin)
                await db.commit()
                print("✅ Admin user created: admin / admin123")
            else:
                print("ℹ️ Admin user already exists")
            break

@app.on_event("shutdown")
async def shutdown_event():
    await close_database_connection()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Gzip compression middleware
# Compress responses > 1000 bytes (1KB) to reduce transfer time
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"], include_in_schema=False)
app.include_router(open_academic_analytics.router, prefix="/open-academic-analytics", tags=["academics"])
app.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
app.include_router(datalakes.router, prefix="/datalakes", tags=["datalakes"])
app.include_router(wikimedia.router, prefix="/wikimedia", tags=["wikimedia"])
app.include_router(annotations.router, prefix="/annotations", tags=["annotations"])
app.include_router(scisciDB.router, prefix="/scisciDB", tags=["scisciDB"])
app.include_router(admin.router, prefix="/admin", tags=["admin"], include_in_schema=False)

# Admin endpoints (secured with admin authentication)
app.include_router(auth.admin_router, prefix="/admin/auth", tags=["admin"], include_in_schema=False)
app.include_router(datasets.admin_router, prefix="/admin/datasets", tags=["admin"], include_in_schema=False)
app.include_router(datalakes.admin_router, prefix="/admin/datalakes", tags=["admin"], include_in_schema=False)
app.include_router(open_academic_analytics.admin_router, prefix="/admin/open-academic-analytics", tags=["admin"], include_in_schema=False)
app.include_router(annotations.admin_router, prefix="/admin/annotations", tags=["admin"], include_in_schema=False)


@app.get("/")
async def root():
    return {"message": "Complex Stories API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


