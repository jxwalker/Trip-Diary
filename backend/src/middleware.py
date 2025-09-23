"""
FastAPI Middleware for Logging and Error Handling
Provides request/response logging, error handling, and correlation ID tracking
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging
import sys
from pathlib import Path

import logging
import uuid

logger = logging.getLogger(__name__)

# Simple correlation ID implementation
_correlation_id = None

def set_correlation_id(correlation_id: str):
    global _correlation_id
    _correlation_id = correlation_id

def get_correlation_id() -> str:
    global _correlation_id
    return _correlation_id or str(uuid.uuid4())

def log_request(method: str, url: str, **kwargs):
    logger.info(f"Request: {method} {url}", extra=kwargs)

def log_response(status_code: int, **kwargs):
    logger.info(f"Response: {status_code}", extra=kwargs)

def log_error(error: str, **kwargs):
    logger.error(f"Error: {error}", extra=kwargs)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging with correlation IDs"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, 
                      call_next: Callable) -> Response:
        # Generate correlation ID
        correlation_id = set_correlation_id()
        
        # Add correlation ID to request state
        request.state.correlation_id = correlation_id
        
        # Log request
        start_time = time.time()
        
        # Extract request info
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        content_length = request.headers.get("content-length", "0")
        
        log_request(
            logger,
            request.method,
            str(request.url),
            client_ip=client_ip,
            user_agent=user_agent,
            content_length=content_length
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log response
            log_response(
                logger,
                response.status_code,
                duration_ms,
                response_size=response.headers.get("content-length", "unknown")
            )
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error
            log_error(logger, e, {
                'request_method': request.method,
                'request_path': str(request.url),
                'duration_ms': duration_ms
            })
            
            # Return error response
            if isinstance(e, HTTPException):
                return JSONResponse(
                    status_code=e.status_code,
                    content={"error": e.detail, 
                            "correlation_id": correlation_id},
                    headers={"X-Correlation-ID": correlation_id}
                )
            else:
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": "Internal server error",
                        "correlation_id": correlation_id,
                        "message": str(e) if logger.level <= logging.DEBUG 
                                  else "An unexpected error occurred"
                    },
                    headers={"X-Correlation-ID": correlation_id}
                )

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for centralized error handling"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, 
                      call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except HTTPException:
            # Let HTTPExceptions pass through
            raise
        except Exception as e:
            # Log unexpected errors
            correlation_id = getattr(request.state, 'correlation_id', 
                                    'unknown')
            
            log_error(logger, e, {
                'request_method': request.method,
                'request_path': str(request.url),
                'correlation_id': correlation_id
            })
            
            # Return generic error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "correlation_id": correlation_id,
                    "message": ("An unexpected error occurred. "
                           "Please check the logs for details.")
                },
                headers={"X-Correlation-ID": correlation_id}
            )

def setup_error_handlers(app):
    """Set up custom error handlers for the FastAPI app"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        correlation_id = getattr(request.state, 'correlation_id', 
                                str(uuid.uuid4())[:8])
        
        logger.warning(
            f"HTTP {exc.status_code}: {exc.detail}",
            extra={
                'event_type': 'http_error',
                'status_code': exc.status_code,
                'detail': exc.detail,
                'path': str(request.url)
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "correlation_id": correlation_id
            },
            headers={"X-Correlation-ID": correlation_id}
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        correlation_id = getattr(request.state, 'correlation_id', 
                                str(uuid.uuid4())[:8])
        
        log_error(logger, exc, {
            'request_path': str(request.url),
            'error_type': 'validation_error'
        })
        
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid input",
                "message": str(exc),
                "correlation_id": correlation_id
            },
            headers={"X-Correlation-ID": correlation_id}
        )
    
    @app.exception_handler(FileNotFoundError)
    async def file_not_found_handler(request: Request, exc: FileNotFoundError):
        correlation_id = getattr(request.state, 'correlation_id', 
                                str(uuid.uuid4())[:8])
        
        logger.warning(
            f"File not found: {str(exc)}",
            extra={
                'event_type': 'file_not_found',
                'path': str(request.url)
            }
        )
        
        return JSONResponse(
            status_code=404,
            content={
                "error": "Resource not found",
                "correlation_id": correlation_id
            },
            headers={"X-Correlation-ID": correlation_id}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        correlation_id = getattr(request.state, 'correlation_id', 
                                str(uuid.uuid4())[:8])
        
        log_error(logger, exc, {
            'request_path': str(request.url),
            'error_type': 'unexpected_error'
        })
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "correlation_id": correlation_id,
                "message": ("An unexpected error occurred. "
                           "Please contact support if the problem persists.")
            },
            headers={"X-Correlation-ID": correlation_id}
        )

def log_startup_info(app_name: str, host: str, port: int, environment: str):
    """Log application startup information"""
    logger.info(
        f"Starting {app_name}",
        extra={
            'event_type': 'app_startup',
            'app_name': app_name,
            'host': host,
            'port': port,
            'environment': environment
        }
    )

def log_shutdown_info(app_name: str):
    """Log application shutdown information"""
    logger.info(
        f"Shutting down {app_name}",
        extra={
            'event_type': 'app_shutdown',
            'app_name': app_name
        }
    )
