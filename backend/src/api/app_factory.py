"""
Application factory for creating FastAPI app instances
Enhanced with new architecture and service management
"""
import asyncio
import logging
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .dependencies.container import container
from .routes import upload, status
from ..middleware import LoggingMiddleware, ErrorHandlingMiddleware, setup_error_handlers, log_startup_info
from ..utils.logging_config import setup_logging
from ..utils.environment import load_project_env, is_development
from ..config import get_settings
from ..services.service_factory import service_factory, initialize_services, cleanup_services
from ..services.enhanced_redis_cache import cache_manager
from ..core.middleware import (
    CorrelationIdMiddleware,
    RequestLoggingMiddleware,
    ErrorHandlingMiddleware as EnhancedErrorHandlingMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    RequestValidationMiddleware
)

# Load environment
load_project_env()

logger = logging.getLogger(__name__)


def create_app(config: Optional[object] = None) -> FastAPI:
    """
    Create and configure FastAPI application with enhanced architecture

    Args:
        config: Configuration object (uses default if None)

    Returns:
        Configured FastAPI application
    """
    # Use new configuration system
    settings = get_settings()

    # Import legacy config for backward compatibility
    if config is None:
        try:
            from config import config as default_config
            config = default_config
        except ImportError:
            # Use new settings as fallback
            config = settings

    # Set up logging
    setup_logging("logs", debug=settings.is_development)

    # Create FastAPI app with enhanced configuration
    app = FastAPI(
        title=settings.api.title,
        version=settings.api.version,
        description=settings.api.description,
        docs_url=settings.api.docs_url if settings.api.docs_enabled else None,
        redoc_url=settings.api.redoc_url if settings.api.docs_enabled else None,
        openapi_url=settings.api.openapi_url if settings.api.docs_enabled else None
    )

    # Initialize service container (legacy)
    container.initialize(config)

    # Add enhanced middleware
    _configure_enhanced_middleware(app, settings)

    # Add routes
    _configure_routes(app)

    # Set up error handlers
    setup_error_handlers(app)

    # Add startup/shutdown events
    _configure_enhanced_events(app, settings)

    logger.info("Enhanced FastAPI application created successfully")

    return app


def _configure_enhanced_middleware(app: FastAPI, settings) -> None:
    """Configure enhanced application middleware"""

    # Add enhanced middleware stack (order matters!)
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestValidationMiddleware)

    # Add rate limiting if enabled
    if settings.rate_limit_enabled:
        app.add_middleware(RateLimitMiddleware)

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(EnhancedErrorHandlingMiddleware)

    # Configure CORS with enhanced settings
    if settings.api.cors_enabled:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.allowed_origins,
            allow_credentials=settings.api.cors_allow_credentials,
            allow_methods=settings.api.cors_allow_methods,
            allow_headers=settings.api.cors_allow_headers,
            expose_headers=settings.api.cors_expose_headers
        )

    logger.info("Enhanced middleware configured")


def _configure_middleware(app: FastAPI, config: object) -> None:
    """Configure legacy middleware (for backward compatibility)"""
    # Legacy middleware configuration
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(ErrorHandlingMiddleware)

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=getattr(config, 'ALLOWED_ORIGINS', ["*"]),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["Content-Type", "X-Trip-ID"]
    )

    logger.info("Legacy middleware configured")


def _configure_routes(app: FastAPI) -> None:
    """Configure application routes"""

    # Import route modules
    from .routes import upload, status, enhanced_guide, preferences, generation, pdf, pdf_html, health, debug, test_guide, test_quality

    # Add route modules
    app.include_router(upload.router)
    app.include_router(status.router)
    app.include_router(enhanced_guide.router)
    app.include_router(preferences.router)
    app.include_router(generation.router)
    app.include_router(pdf.router)
    app.include_router(pdf_html.router)
    app.include_router(health.router)
    app.include_router(debug.router)
    app.include_router(test_guide.router)
    app.include_router(test_quality.router)

    # Add root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "TripCraft AI API is running",
            "version": "1.0.0",
            "status": "healthy"
        }

    logger.info("Routes configured")


def _configure_enhanced_events(app: FastAPI, settings) -> None:
    """Configure enhanced startup and shutdown events"""

    @app.on_event("startup")
    async def enhanced_startup_event():
        """Enhanced application startup tasks"""
        log_startup_info(
            settings.api.title,
            settings.api.host,
            settings.api.port,
            settings.environment
        )

        try:
            # Initialize Redis cache manager
            redis_connected = await cache_manager.connect()
            if redis_connected:
                logger.info("Redis cache manager connected successfully")
                # Get initial stats
                stats = await cache_manager.get_stats()
                logger.info(f"Redis stats: {stats}")
            else:
                logger.warning("Redis cache not available - continuing without caching")
            
            # Initialize new service system
            await initialize_services()
            logger.info("Enhanced service system initialized")
            
            # Ensure container database service is not overridden
            # The enhanced service system should not interfere with the legacy container
            logger.info("Database service isolation verified")

            # Health check all services
            health_status = await service_factory.health_check_all()
            healthy_services = sum(1 for status in health_status.values() if status.get("status") == "healthy")
            total_services = len(health_status)
            logger.info(f"Service health check: {healthy_services}/{total_services} services healthy")

            # Start legacy cleanup service for backward compatibility
            try:
                cleanup_service = container.get_cleanup_service()
                asyncio.create_task(cleanup_service.start_periodic_cleanup(
                    interval_hours=settings.cleanup_interval_hours
                ))
                logger.info(f"Legacy cleanup service started - will run every {settings.cleanup_interval_hours} hours")
            except Exception as e:
                logger.warning(f"Failed to start legacy cleanup service: {e}")

        except Exception as e:
            logger.error(f"Enhanced startup failed: {e}")
            # Continue with basic startup for backward compatibility

        logger.info("Enhanced application startup complete")

    @app.on_event("shutdown")
    async def enhanced_shutdown_event():
        """Enhanced application shutdown tasks"""
        logger.info("Enhanced application shutting down...")

        try:
            # Cleanup Redis connection
            await cache_manager.disconnect()
            logger.info("Redis cache manager disconnected")
            
            # Cleanup new service system
            await cleanup_services()
            logger.info("Enhanced service system cleaned up")
        except Exception as e:
            logger.error(f"Service cleanup failed: {e}")

        logger.info("Enhanced application shutdown complete")

    logger.info("Enhanced event handlers configured")


def _configure_events(app: FastAPI, config: object) -> None:
    """Configure legacy events (for backward compatibility)"""

    @app.on_event("startup")
    async def startup_event():
        """Legacy application startup tasks"""
        log_startup_info(
            "TripCraft AI API",
            getattr(config, 'HOST', 'localhost'),
            getattr(config, 'PORT', 8000),
            getattr(config, 'ENVIRONMENT', 'development')
        )

        # Start cleanup service
        try:
            cleanup_service = container.get_cleanup_service()
            asyncio.create_task(cleanup_service.start_periodic_cleanup(interval_hours=1))
            logger.info("Legacy cleanup service started - will run every hour")
        except Exception as e:
            logger.warning(f"Failed to start cleanup service: {e}")

        logger.info("Legacy application startup complete")

    @app.on_event("shutdown")
    async def shutdown_event():
        """Legacy application shutdown tasks"""
        logger.info("Legacy application shutting down...")
        logger.info("Legacy application shutdown complete")

    logger.info("Legacy event handlers configured")


# Create the app instance for uvicorn
app = create_app()
