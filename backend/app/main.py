from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.utils import setup_logging
from app.routes import papers_router, users_router
from app.services import (
    get_service_bus_service,
    get_cosmos_db_service,
    get_blob_storage_service,
)

# Setup logging
setup_logging(debug=settings.DEBUG)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager for startup/shutdown"""
    # Startup
    logger.info("Starting up application...")
    try:
        # Initialize Azure services
        await get_service_bus_service()
        await get_cosmos_db_service()
        await get_blob_storage_service()
        logger.info("All Azure services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    # Services will be cleaned up as needed


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Generate interview question papers using AI agents and Azure services",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(papers_router)
app.include_router(users_router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "debug": settings.DEBUG,
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Interview Question Paper Generator",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        debug=settings.DEBUG,
    )
