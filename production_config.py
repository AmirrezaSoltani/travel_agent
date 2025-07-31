#!/usr/bin/env python3
"""
Production Configuration for AI Travel Recommender Agent
تنظیمات تولید برای سیستم هوشمند پیشنهاد مسیر سفر
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Production settings
PRODUCTION = True
DEBUG = False

# Server settings
HOST = "0.0.0.0"
PORT = 8000
WORKERS = 4

# Database settings
DATABASE_URL = "sqlite:///./ai_travel_agent.db"

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALLOWED_HOSTS = ["37.152.188.62", "agent.amirrezasoltani.ir", "localhost", "127.0.0.1", "*"]

# Logging settings
LOG_LEVEL = "INFO"
LOG_FILE = BASE_DIR / "logs" / "app.log"

# Static files
STATIC_DIR = BASE_DIR / "app" / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# API settings
API_PREFIX = "/api"
API_VERSION = "v1"

# Map settings
MAP_CENTER = [32.4279, 53.6880]  # Iran center
MAP_ZOOM = 6
OPENSTREETMAP_URL = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"

# Chat settings
CHAT_HISTORY_LIMIT = 50
MAX_MESSAGE_LENGTH = 1000

# Route settings
DEFAULT_FUEL_COST_PER_KM = 500  # tomans
AVERAGE_SPEED_KMH = 80

# Attraction settings
MAX_ATTRACTIONS_PER_ROUTE = 10
MIN_ATTRACTION_RATING = 3.0

# Language settings
DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ["en", "fa"]

# Cache settings
CACHE_TTL = 3600  # 1 hour
CACHE_ENABLED = True

# Monitoring settings
HEALTH_CHECK_ENDPOINT = "/health"
METRICS_ENDPOINT = "/metrics"

# File upload settings
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = [".jpg", ".jpeg", ".png", ".gif"]

# Rate limiting
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 3600  # 1 hour

# Email settings (if needed)
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# External APIs
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
TRANSLATION_API_KEY = os.getenv("TRANSLATION_API_KEY", "")

# Performance settings
CONNECTION_POOL_SIZE = 20
MAX_CONNECTIONS = 100
REQUEST_TIMEOUT = 30

# Backup settings
BACKUP_ENABLED = True
BACKUP_INTERVAL = 86400  # 24 hours
BACKUP_RETENTION_DAYS = 7

# SSL/TLS settings
SSL_ENABLED = False
SSL_CERT_FILE = ""
SSL_KEY_FILE = ""

# Development overrides
if os.getenv("DEVELOPMENT"):
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    CACHE_ENABLED = False

# Environment-specific settings
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

if ENVIRONMENT == "development":
    DEBUG = True
    LOG_LEVEL = "DEBUG"
elif ENVIRONMENT == "staging":
    DEBUG = False
    LOG_LEVEL = "INFO"
elif ENVIRONMENT == "production":
    DEBUG = False
    LOG_LEVEL = "WARNING"

# Create necessary directories
def create_directories():
    """Create necessary directories for the application"""
    directories = [
        BASE_DIR / "logs",
        BASE_DIR / "data",
        BASE_DIR / "uploads",
        BASE_DIR / "backups",
        STATIC_DIR,
        TEMPLATES_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Initialize directories
create_directories()

# Export settings
__all__ = [
    "PRODUCTION", "DEBUG", "HOST", "PORT", "WORKERS",
    "DATABASE_URL", "SECRET_KEY", "ALLOWED_HOSTS",
    "LOG_LEVEL", "LOG_FILE", "STATIC_DIR", "TEMPLATES_DIR",
    "API_PREFIX", "API_VERSION", "MAP_CENTER", "MAP_ZOOM",
    "CHAT_HISTORY_LIMIT", "MAX_MESSAGE_LENGTH",
    "DEFAULT_FUEL_COST_PER_KM", "AVERAGE_SPEED_KMH",
    "MAX_ATTRACTIONS_PER_ROUTE", "MIN_ATTRACTION_RATING",
    "DEFAULT_LANGUAGE", "SUPPORTED_LANGUAGES",
    "CACHE_TTL", "CACHE_ENABLED", "HEALTH_CHECK_ENDPOINT",
    "METRICS_ENDPOINT", "MAX_FILE_SIZE", "ALLOWED_FILE_TYPES",
    "RATE_LIMIT_REQUESTS", "RATE_LIMIT_WINDOW",
    "CONNECTION_POOL_SIZE", "MAX_CONNECTIONS", "REQUEST_TIMEOUT",
    "BACKUP_ENABLED", "BACKUP_INTERVAL", "BACKUP_RETENTION_DAYS",
    "SSL_ENABLED", "ENVIRONMENT"
] 