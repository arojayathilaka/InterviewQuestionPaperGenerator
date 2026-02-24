#!/usr/bin/env python3
"""
Interview Question Paper Generator - FastAPI Backend
Entry point for running the application
"""

if __name__ == "__main__":
    import uvicorn
    from app.config import settings
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
