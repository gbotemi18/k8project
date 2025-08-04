#!/usr/bin/env python3
"""
IP Reversal Web Application
Main entry point for the FastAPI application
"""

import uvicorn
from src.config import settings
from src.api import app

if __name__ == "__main__":
    uvicorn.run(
        "src.api:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    ) 