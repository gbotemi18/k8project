from fastapi import FastAPI, Request, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from src.config import settings
from src.database import get_db, init_db
from src.services import IPAddressService
from src.utils import get_client_ip
from src.models import IPAddressResponse, IPAddressHistoryResponse, HealthCheckResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A web application that reverses IP addresses and stores them in a database",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Templates for web interface
templates = Jinja2Templates(directory="src/templates")


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    try:
        init_db()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise


@app.get("/", response_class=HTMLResponse)
async def web_interface(request: Request, db: Session = Depends(get_db)):
    """Web interface showing the reversed IP address"""
    try:
        client_ip = get_client_ip(request)
        user_agent = request.headers.get("User-Agent")
        ip_info = IPAddressService.process_ip_request(db, client_ip, user_agent)
        stats = IPAddressService.get_statistics(db)
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "ip_info": ip_info,
            "stats": stats,
            "app_name": settings.app_name,
            "app_version": settings.app_version
        })
    except Exception as e:
        logger.error(f"Error in web interface: {e}")
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": str(e),
            "app_name": settings.app_name
        })


@app.get("/api/ip", response_model=IPAddressResponse)
async def get_reversed_ip(request: Request, db: Session = Depends(get_db)):
    """API endpoint to get the reversed IP address"""
    try:
        client_ip = get_client_ip(request)
        user_agent = request.headers.get("User-Agent")
        ip_info = IPAddressService.process_ip_request(db, client_ip, user_agent)
        return IPAddressResponse(**ip_info)
    except Exception as e:
        logger.error(f"Error in API endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history", response_model=IPAddressHistoryResponse)
async def get_ip_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get IP address history"""
    try:
        history = IPAddressService.get_ip_history(db, limit, offset)
        return IPAddressHistoryResponse(**history)
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_statistics(db: Session = Depends(get_db)):
    """Get application statistics"""
    try:
        stats = IPAddressService.get_statistics(db)
        return stats
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health", response_model=HealthCheckResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        db_status = IPAddressService.check_database_health(db)
        return HealthCheckResponse(
            status="healthy" if db_status == "healthy" else "unhealthy",
            version=settings.app_version,
            timestamp=datetime.utcnow(),
            database_status=db_status
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheckResponse(
            status="unhealthy",
            version=settings.app_version,
            timestamp=datetime.utcnow(),
            database_status="unhealthy"
        ) 