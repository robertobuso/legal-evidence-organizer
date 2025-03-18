from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
import os

from app.database import Base, engine, get_db
from app.routes import upload, emails, search, timeline, evidence, report
from app.config import APP_NAME, APP_VERSION, DEBUG
from app.utils.logger import app_logger

# Create app instance
app = FastAPI(
    title=APP_NAME,
    description="API for Legal Evidence Organizer application",
    version=APP_VERSION,
    debug=DEBUG
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(emails.router, prefix="/api", tags=["Emails"])
app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(timeline.router, prefix="/api", tags=["Timeline"])
app.include_router(evidence.router, prefix="/api", tags=["Evidence"])
app.include_router(report.router, prefix="/api", tags=["Report"])

# Create database tables
@app.on_event("startup")
async def startup():
    app_logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    app_logger.info("Creating database tables if they don't exist")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Health check endpoint
@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": APP_NAME,
        "version": APP_VERSION
    }

# Root endpoint
@app.get("/", tags=["Root"])
async def read_root():
    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "documentation": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)