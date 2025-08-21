"""
Enhanced middleware for TripCraft AI
Improved request handling, security, and monitoring
"""
import time
import json
import uuid
from typing import Callable, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .exceptions import (
    TripCraftException, 
    get_status_code, 
    create_error_response,
    RateLimitError,
    ValidationError
)
from ..config import get_settings

logger = logging.getLogger(__name__)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Add correlation ID to all requests"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate or extract correlation ID
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        
        # Add to request state
        request.state.correlation_id = correlation_id
        
        # Process request
        response = await call_next(request)
        
        # Add to response headers
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Enhanced request/response logging"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.settings = get_settings()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        correlation_id = getattr(request.state, 'correlation_id', 'unknown')
        
        # Log request
        await self._log_request(request, correlation_id)
        
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log response
            await self._log_response(request, response, duration_ms, correlation_id)
            
            return response
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            await self._log_error(request, e, duration_ms, correlation_id)
            raise
    
    async def _log_request(self, request: Request, correlation_id: str):
        """Log incoming request"""
        if not self.settings.logging.request_logging_enabled:
            return
        
        log_data = {
            "event": "request_start",
            "correlation_id": correlation_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", "unknown"),
            "content_length": request.headers.get("content-length", "0"),
            "timestamp": datetime.now().isoformat()
        }
        
        # Add headers if enabled
        if self.settings.logging.request_log_headers:
            log_data["headers"] = dict(request.headers)
        
        logger.info("Request started", extra=log_data)
    
    async def _log_response(
        self, 
        request: Request, 
        response: Response, 
        duration_ms: float, 
        correlation_id: str
    ):
        """Log response"""
        log_data = {
            "event": "request_complete",
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "response_size": response.headers.get("content-length", "unknown"),
            "timestamp": datetime.now().isoformat()
        }
        
        # Check if this is a slow request
        if self.settings.logging.should_log_slow_request(duration_ms):
            log_data["slow_request"] = True
            logger.warning("Slow request detected", extra=log_data)
        else:
            logger.info("Request completed", extra=log_data)
    
    async def _log_error(
        self, 
        request: Request, 
        error: Exception, 
        duration_ms: float, 
        correlation_id: str
    ):
        """Log request error"""
        log_data = {
            "event": "request_error",
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "duration_ms": round(duration_ms, 2),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.error("Request failed", extra=log_data, exc_info=True)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Enhanced error handling with custom exceptions"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except HTTPException:
            # Let FastAPI handle HTTPExceptions
            raise
        except TripCraftException as e:
            # Handle custom exceptions
            return await self._handle_tripcraft_exception(request, e)
        except Exception as e:
            # Handle unexpected exceptions
            return await self._handle_unexpected_exception(request, e)
    
    async def _handle_tripcraft_exception(
        self, 
        request: Request, 
        exception: TripCraftException
    ) -> JSONResponse:
        """Handle custom TripCraft exceptions"""
        correlation_id = getattr(request.state, 'correlation_id', 'unknown')
        
        # Update correlation ID in exception if not set
        if not exception.correlation_id:
            exception.correlation_id = correlation_id
        
        status_code = get_status_code(exception)
        response_data = exception.to_dict()
        
        logger.error(
            f"TripCraft exception: {exception.error_code}",
            extra={
                "correlation_id": correlation_id,
                "exception_type": type(exception).__name__,
                "status_code": status_code,
                "error_details": response_data
            }
        )
        
        return JSONResponse(
            status_code=status_code,
            content=response_data,
            headers={"X-Correlation-ID": correlation_id}
        )
    
    async def _handle_unexpected_exception(
        self, 
        request: Request, 
        exception: Exception
    ) -> JSONResponse:
        """Handle unexpected exceptions"""
        correlation_id = getattr(request.state, 'correlation_id', 'unknown')
        
        logger.error(
            f"Unexpected exception: {type(exception).__name__}",
            extra={
                "correlation_id": correlation_id,
                "exception_message": str(exception),
                "request_path": request.url.path,
                "request_method": request.method
            },
            exc_info=True
        )
        
        # Create standardized error response
        response_data = create_error_response(exception)
        response_data["correlation_id"] = correlation_id
        
        return JSONResponse(
            status_code=500,
            content=response_data,
            headers={"X-Correlation-ID": correlation_id}
        )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.settings = get_settings()
        self.request_counts: Dict[str, Dict[str, Any]] = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not self.settings.rate_limit_enabled:
            return await call_next(request)
        
        client_ip = self._get_client_ip(request)
        
        # Check rate limit
        if await self._is_rate_limited(client_ip):
            raise RateLimitError(
                message="Rate limit exceeded",
                limit=self.settings.rate_limit_requests,
                window=self.settings.rate_limit_window,
                retry_after=self.settings.rate_limit_window
            )
        
        # Record request
        await self._record_request(client_ip)
        
        return await call_next(request)
    
    async def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if client is rate limited"""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.settings.rate_limit_window)
        
        if client_ip not in self.request_counts:
            return False
        
        client_data = self.request_counts[client_ip]
        
        # Clean old requests
        client_data["requests"] = [
            req_time for req_time in client_data["requests"]
            if req_time > window_start
        ]
        
        return len(client_data["requests"]) >= self.settings.rate_limit_requests
    
    async def _record_request(self, client_ip: str):
        """Record a request for rate limiting"""
        now = datetime.now()
        
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = {"requests": []}
        
        self.request_counts[client_ip]["requests"].append(now)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        return request.client.host if request.client else "unknown"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers.update({
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'",
        })
        
        return response


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Validate request size and content"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.settings = get_settings()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length:
            size_mb = int(content_length) / (1024 * 1024)
            if size_mb > self.settings.api.max_request_size / (1024 * 1024):
                raise ValidationError(
                    message="Request too large",
                    details={"max_size_mb": self.settings.api.max_request_size / (1024 * 1024)}
                )
        
        return await call_next(request)
