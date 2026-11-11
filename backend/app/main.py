"""
Complexhibit API - FastAPI Application

Provides REST API endpoints for the OntoExhibit knowledge graph.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import create_tables
from app.dependencies import get_current_user
from app.routers import artworks, exhibitions, institutions, misc, persons, auth, catalogs, companies, map, example_queries, metrics
from app.core.seeding import seed_example_queries, seed_admins

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("complexhibit")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("complexhibit")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: create database tables
    try:
        create_tables()
        logger.info("Database tables created successfully")

        # Seed default data
        seed_admins()
        seed_example_queries()

        logger.info("Application initialized successfully")
    except Exception as e:
        logger.warning(
            "Database initialization error (may be expected if DB not ready): %s", e
        )
    yield
    # Shutdown: nothing to do


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Bienvenido a la API de Complexhibit, tu puerta de entrada a una experiencia excepcional "
        "en el mundo del arte y la cultura. Nuestra API te ofrece acceso a una rica colección de "
        "datos y recursos relacionados con exposiciones, obras maestras y eventos culturales de "
        "todo el mundo."
    ),
    version=settings.VERSION,
    openapi_url=f"{settings.DEPLOY_PATH}/openapi.json",
    docs_url=f"{settings.DEPLOY_PATH}/docs",
    lifespan=lifespan,
)

# CORS configuration - Restrict to known origins (configurable via CORS_ORIGINS env var).
# Falls back to localhost dev + the production domain when the env var is unset.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# Include routers
app.include_router(auth.router, prefix=settings.DEPLOY_PATH)
app.include_router(persons.router)
app.include_router(institutions.router)
app.include_router(exhibitions.router)
app.include_router(artworks.router)
app.include_router(misc.router)
app.include_router(catalogs.router)
app.include_router(companies.router)
app.include_router(map.router)
app.include_router(example_queries.router)
app.include_router(metrics.router)

@app.get(f"{settings.DEPLOY_PATH}/", tags=["root"])
async def root():
    """Health check endpoint."""
    return {"message": "Complexhibit API is running", "version": settings.VERSION}


@app.get(f"{settings.DEPLOY_PATH}/users/me", response_model=dict, tags=["users"])
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """Get current user info (legacy endpoint)."""
    return {"user": current_user, "message": "User info retrieval mocked"}


@app.get(f"{settings.DEPLOY_PATH}/secure-endpoint", tags=["users"])
async def secure_endpoint(current_user: dict = Depends(get_current_user)):
    """Test secure endpoint (legacy)."""
    return {"detail": "This is a secure endpoint", "user_id": current_user}
