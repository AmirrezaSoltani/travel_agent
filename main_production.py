#!/usr/bin/env python3
"""
AI Travel Recommender Agent - Production Server
سیستم هوشمند پیشنهاد مسیر سفر - سرور تولید
"""

import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Add project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Import production config
try:
    from production_config import *
except ImportError:
    # Fallback to development settings
    PRODUCTION = False
    DEBUG = True
    HOST = "0.0.0.0"
    PORT = 8000
    SECRET_KEY = "dev-secret-key"
    ALLOWED_HOSTS = ["*"]
    DEFAULT_LANGUAGE = "en"

# Import application modules
from app.core.config import settings
from app.database import engine, Base
from app.api.routes import router as api_router
from app.api.chat import router as chat_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL if 'LOG_LEVEL' in locals() else 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE if 'LOG_FILE' in locals() else 'app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {e}")

# Create FastAPI application
app = FastAPI(
    title="AI Travel Recommender Agent",
    description="سیستم هوشمند پیشنهاد مسیر سفر",
    version="1.0.0",
    docs_url="/docs" if not PRODUCTION else None,
    redoc_url="/redoc" if not PRODUCTION else None
)

# Security middleware
if PRODUCTION and ALLOWED_HOSTS != ["*"]:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=ALLOWED_HOSTS
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not PRODUCTION else ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
try:
    static_dir = STATIC_DIR if 'STATIC_DIR' in locals() else project_root / "app" / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logger.info(f"Static files mounted from: {static_dir}")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")

# Templates
try:
    templates_dir = TEMPLATES_DIR if 'TEMPLATES_DIR' in locals() else project_root / "templates"
    templates = Jinja2Templates(directory=str(templates_dir))
    logger.info(f"Templates loaded from: {templates_dir}")
except Exception as e:
    logger.error(f"Could not load templates: {e}")
    templates = None

# Include routers
app.include_router(api_router, prefix="/api")
app.include_router(chat_router, prefix="/chat")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": ENVIRONMENT if 'ENVIRONMENT' in locals() else "production"
    }

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Basic metrics endpoint"""
    return {
        "uptime": "running",
        "requests": 0,
        "errors": 0
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={"error": "صفحه مورد نظر یافت نشد", "path": str(request.url.path)}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "خطای داخلی سرور", "message": "لطفاً بعداً تلاش کنید"}
    )

# Main page routes
@app.get("/")
async def home(request: Request):
    """صفحه اصلی"""
    if not templates:
        return JSONResponse(content={"error": "Templates not available"})
    
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logger.error(f"Error rendering home page: {e}")
        return JSONResponse(content={"error": "خطا در بارگذاری صفحه اصلی"})

@app.get("/map")
async def map_view(request: Request):
    """صفحه نقشه"""
    if not templates:
        return JSONResponse(content={"error": "Templates not available"})
    
    try:
        return templates.TemplateResponse("map.html", {"request": request})
    except Exception as e:
        logger.error(f"Error rendering map page: {e}")
        return JSONResponse(content={"error": "خطا در بارگذاری صفحه نقشه"})

@app.get("/chat")
async def chat_view(request: Request):
    """صفحه چت"""
    if not templates:
        return JSONResponse(content={"error": "Templates not available"})
    
    try:
        return templates.TemplateResponse("chat.html", {"request": request})
    except Exception as e:
        logger.error(f"Error rendering chat page: {e}")
        return JSONResponse(content={"error": "خطا در بارگذاری صفحه چت"})

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("🚀 AI Travel Recommender Agent starting up...")
    logger.info(f"Environment: {ENVIRONMENT if 'ENVIRONMENT' in locals() else 'production'}")
    logger.info(f"Debug mode: {DEBUG if 'DEBUG' in locals() else False}")
    logger.info(f"Production mode: {PRODUCTION if 'PRODUCTION' in locals() else False}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("🛑 AI Travel Recommender Agent shutting down...")

if __name__ == "__main__":
    # Production server configuration
    uvicorn.run(
        "main_production:app",
        host=HOST,
        port=PORT,
        workers=WORKERS if 'WORKERS' in locals() else 1,
        log_level=LOG_LEVEL.lower() if 'LOG_LEVEL' in locals() else "info",
        access_log=True,
        reload=DEBUG if 'DEBUG' in locals() else False
    ) 