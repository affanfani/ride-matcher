from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
from contextlib import asynccontextmanager

from app.api.api import api_router
from app.db.session import init_db, close_db
from app.core.config import get_settings

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting Ride Matcher API...")
    await init_db()
    logger.info("✅ Database initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Ride Matcher API...")
    await close_db()
    logger.info("✅ Application shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="Ride Matcher API",
    version="1.0.0",
    description="A simplified ride-matching API built with FastAPI",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Ride Matcher API",
        "docs": "/docs",
        "health": "/health"
    }