"""
Campus Resource Sharing & Utilization Platform — FastAPI Application Entry Point.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.services.cloudant_service import db
from app.routes import auth, resources, bookings, analytics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info("Starting Campus Resource Platform API...")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Using Cloudant: {settings.use_cloudant}")

    try:
        await db.initialize()
        logger.info("Database initialized successfully")

        # Seed default admin user if none exists
        await _seed_default_data()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        logger.warning("App starting without database — some features may not work")

    yield

    # Shutdown
    logger.info("Shutting down...")
    await db.close()


app = FastAPI(
    title="Campus Resource Platform API",
    description="Cloud-Based Campus Resource Sharing & Utilization Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(resources.router)
app.include_router(bookings.router)
app.include_router(analytics.router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring and load balancer."""
    return {
        "status": "healthy",
        "service": "campus-resource-platform",
        "version": "1.0.0",
        "environment": settings.APP_ENV,
    }


@app.get("/")
async def root():
    """Root endpoint — API info."""
    return {
        "message": "Campus Resource Sharing & Utilization Platform API",
        "docs": "/api/docs",
        "health": "/api/health",
    }


async def _seed_default_data():
    """Seed default admin user and sample resources on first run."""
    from app.services.cloudant_service import DB_USERS, DB_RESOURCES
    from app.services.auth_service import hash_password
    from datetime import datetime, timezone

    # Check if admin exists
    admins = await db.find_documents(DB_USERS, {"type": "user", "role": "admin"})
    if admins:
        logger.info("Admin user already exists, skipping seed.")
        return

    logger.info("Seeding default data...")
    now = datetime.now(timezone.utc).isoformat()

    # Create default admin
    admin_doc = {
        "type": "user",
        "name": "Campus Admin",
        "email": "admin@campus.edu",
        "password_hash": hash_password("admin123"),
        "role": "admin",
        "department": "Administration",
        "created_at": now,
    }
    admin = await db.create_document(DB_USERS, admin_doc)
    logger.info(f"Created default admin: admin@campus.edu / admin123")

    # Create sample resources
    sample_resources = [
        {
            "type": "resource",
            "name": "Seminar Hall A",
            "category": "hall",
            "location": "Block A, Floor 2",
            "capacity": 200,
            "amenities": ["projector", "AC", "whiteboard", "mic system"],
            "description": "Large seminar hall with modern AV equipment, ideal for workshops and conferences.",
            "available": True,
            "created_by": admin["_id"],
            "created_at": now,
        },
        {
            "type": "resource",
            "name": "Computer Lab 1",
            "category": "lab",
            "location": "Block B, Floor 1",
            "capacity": 60,
            "amenities": ["computers", "AC", "projector", "internet"],
            "description": "60-seat computer lab with high-speed internet and latest hardware.",
            "available": True,
            "created_by": admin["_id"],
            "created_at": now,
        },
        {
            "type": "resource",
            "name": "Conference Room 101",
            "category": "classroom",
            "location": "Block A, Floor 1",
            "capacity": 30,
            "amenities": ["projector", "AC", "whiteboard", "video conferencing"],
            "description": "Smart conference room with video conferencing and presentation facilities.",
            "available": True,
            "created_by": admin["_id"],
            "created_at": now,
        },
        {
            "type": "resource",
            "name": "Physics Laboratory",
            "category": "lab",
            "location": "Block C, Floor 2",
            "capacity": 40,
            "amenities": ["lab equipment", "AC", "safety gear"],
            "description": "Fully equipped physics laboratory for experiments and practical sessions.",
            "available": True,
            "created_by": admin["_id"],
            "created_at": now,
        },
        {
            "type": "resource",
            "name": "Sports Complex - Indoor Court",
            "category": "sports",
            "location": "Sports Block",
            "capacity": 50,
            "amenities": ["basketball court", "badminton", "changing rooms"],
            "description": "Multi-purpose indoor sports court for basketball, badminton, and other activities.",
            "available": True,
            "created_by": admin["_id"],
            "created_at": now,
        },
        {
            "type": "resource",
            "name": "Portable Projector Set",
            "category": "equipment",
            "location": "Admin Office, Block A",
            "capacity": 1,
            "amenities": ["projector", "screen", "HDMI cable", "carrying case"],
            "description": "Portable projector with retractable screen — available for checkout.",
            "available": True,
            "created_by": admin["_id"],
            "created_at": now,
        },
    ]

    for resource in sample_resources:
        await db.create_document(DB_RESOURCES, resource)

    logger.info(f"Seeded {len(sample_resources)} sample resources.")
