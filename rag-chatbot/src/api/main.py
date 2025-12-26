"""
FastAPI Application Entry Point

Initializes the RAG chatbot API server with middleware, routes, and configuration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from ..config.settings import get_settings
from .middleware.rate_limit import RateLimitMiddleware
from .middleware.error_handling import ErrorHandlingMiddleware


# ============================================================================
# Application Setup
# ============================================================================

def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        Configured FastAPI app instance
    """
    settings = get_settings()

    # Configure logging
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    # Create FastAPI app
    app = FastAPI(
        title="RAG Chatbot API",
        description="Retrieval-Augmented Generation chatbot for Physical AI & Humanoid Robotics book",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ========================================================================
    # Middleware Configuration
    # ========================================================================

    # CORS middleware (must be first)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        max_age=600,  # Cache preflight requests for 10 minutes
    )

    # Error handling middleware
    app.add_middleware(ErrorHandlingMiddleware)

    # Rate limiting middleware
    app.add_middleware(RateLimitMiddleware)

    logger.info("Middleware configured successfully")

    # ========================================================================
    # Route Registration
    # ========================================================================

    # Import routes here to avoid circular imports
    from .routes import health, query

    # Register route modules
    app.include_router(health.router, prefix="/v1", tags=["Health"])
    app.include_router(query.router, prefix="/v1", tags=["Query"])

    logger.info("Routes registered successfully")

    # ========================================================================
    # Startup/Shutdown Events
    # ========================================================================

    @app.on_event("startup")
    async def startup_event():
        """Run tasks on application startup."""
        logger.info("=" * 60)
        logger.info("RAG Chatbot API Server Starting")
        logger.info("=" * 60)
        logger.info(f"Environment: {settings.log_level}")
        logger.info(f"Qdrant Collection: {settings.qdrant_collection}")
        logger.info(f"Rate Limit: {settings.rate_limit_queries_per_minute} queries/min")
        logger.info(f"Allowed Origins: {', '.join(settings.allowed_origins)}")
        logger.info("=" * 60)

        # Verify connections
        from ..services.storage import get_storage_service

        storage = get_storage_service(settings)

        # Check database health
        health_status = await storage.check_all_services_health()

        for service_name, status in health_status.items():
            if status["status"] == "healthy":
                logger.info(f"✅ {service_name.capitalize()}: Connected ({status['latency_ms']}ms)")
            else:
                error = status.get("error", "Unknown error")
                logger.error(f"❌ {service_name.capitalize()}: Connection failed - {error}")

        logger.info("Startup complete")

    @app.on_event("shutdown")
    async def shutdown_event():
        """Run cleanup tasks on application shutdown."""
        logger.info("Shutting down RAG Chatbot API Server")

        # Cleanup storage service
        from ..services.storage import get_storage_service

        try:
            storage = get_storage_service(settings)
            storage.close()
            logger.info("✅ Storage service closed")
        except Exception as e:
            logger.error(f"❌ Error closing storage service: {e}")

        logger.info("Shutdown complete")

    # ========================================================================
    # Root Endpoint
    # ========================================================================

    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "RAG Chatbot API",
            "version": "1.0.0",
            "description": "Retrieval-Augmented Generation chatbot for Physical AI & Humanoid Robotics book",
            "endpoints": {
                "health": "/v1/health",
                "docs": "/docs",
                "redoc": "/redoc",
            },
            "status": "operational",
        }

    return app


# ============================================================================
# App Instance
# ============================================================================

# Create app instance
app = create_app()


# ============================================================================
# Entry Point for Development Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    settings = get_settings()

    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,  # Enable auto-reload for development
        log_level=settings.log_level.lower(),
    )
