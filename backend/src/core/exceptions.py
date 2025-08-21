"""
Custom exceptions for TripCraft AI
Standardized error handling with proper HTTP status codes
"""
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class TripCraftException(Exception):
    """Base exception for TripCraft AI"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.timestamp = datetime.now().isoformat()
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary"""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp
        }


class ValidationError(TripCraftException):
    """Validation error - 400 Bad Request"""
    
    def __init__(
        self,
        message: str = "Validation failed",
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if field:
            details['field'] = field
        if value is not None:
            details['value'] = str(value)
        
        super().__init__(message, details=details, **kwargs)


class NotFoundError(TripCraftException):
    """Resource not found error - 404 Not Found"""
    
    def __init__(
        self,
        message: str = "Resource not found",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if resource_type:
            details['resource_type'] = resource_type
        if resource_id:
            details['resource_id'] = resource_id
        
        super().__init__(message, details=details, **kwargs)


class ProcessingError(TripCraftException):
    """Processing error - 422 Unprocessable Entity"""
    
    def __init__(
        self,
        message: str = "Processing failed",
        stage: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if stage:
            details['processing_stage'] = stage
        
        super().__init__(message, details=details, **kwargs)


class ServiceError(TripCraftException):
    """External service error - 502 Bad Gateway"""
    
    def __init__(
        self,
        message: str = "External service error",
        service_name: Optional[str] = None,
        service_response: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if service_name:
            details['service'] = service_name
        if service_response:
            details['service_response'] = service_response
        
        super().__init__(message, details=details, **kwargs)


class ConfigurationError(TripCraftException):
    """Configuration error - 500 Internal Server Error"""
    
    def __init__(
        self,
        message: str = "Configuration error",
        config_key: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if config_key:
            details['config_key'] = config_key
        
        super().__init__(message, details=details, **kwargs)


class AuthenticationError(TripCraftException):
    """Authentication error - 401 Unauthorized"""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        **kwargs
    ):
        super().__init__(message, **kwargs)


class AuthorizationError(TripCraftException):
    """Authorization error - 403 Forbidden"""
    
    def __init__(
        self,
        message: str = "Access denied",
        required_permission: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if required_permission:
            details['required_permission'] = required_permission
        
        super().__init__(message, details=details, **kwargs)


class RateLimitError(TripCraftException):
    """Rate limit exceeded error - 429 Too Many Requests"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit: Optional[int] = None,
        window: Optional[int] = None,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if limit:
            details['limit'] = limit
        if window:
            details['window_seconds'] = window
        if retry_after:
            details['retry_after_seconds'] = retry_after
        
        super().__init__(message, details=details, **kwargs)


class DatabaseError(TripCraftException):
    """Database operation error - 500 Internal Server Error"""
    
    def __init__(
        self,
        message: str = "Database operation failed",
        operation: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if operation:
            details['operation'] = operation
        
        super().__init__(message, details=details, **kwargs)


class FileError(TripCraftException):
    """File operation error - 422 Unprocessable Entity"""
    
    def __init__(
        self,
        message: str = "File operation failed",
        file_path: Optional[str] = None,
        file_type: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if file_path:
            details['file_path'] = file_path
        if file_type:
            details['file_type'] = file_type
        
        super().__init__(message, details=details, **kwargs)


class TimeoutError(TripCraftException):
    """Operation timeout error - 408 Request Timeout"""
    
    def __init__(
        self,
        message: str = "Operation timed out",
        timeout_seconds: Optional[int] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if timeout_seconds:
            details['timeout_seconds'] = timeout_seconds
        if operation:
            details['operation'] = operation
        
        super().__init__(message, details=details, **kwargs)


# HTTP Status Code Mapping
EXCEPTION_STATUS_MAP = {
    ValidationError: 400,
    NotFoundError: 404,
    ProcessingError: 422,
    ServiceError: 502,
    ConfigurationError: 500,
    AuthenticationError: 401,
    AuthorizationError: 403,
    RateLimitError: 429,
    DatabaseError: 500,
    FileError: 422,
    TimeoutError: 408,
    TripCraftException: 500,  # Default for base exception
}


def get_status_code(exception: Exception) -> int:
    """Get HTTP status code for exception"""
    return EXCEPTION_STATUS_MAP.get(type(exception), 500)


def create_error_response(exception: Exception) -> Dict[str, Any]:
    """Create standardized error response"""
    if isinstance(exception, TripCraftException):
        return exception.to_dict()
    
    # Handle non-TripCraft exceptions
    return {
        "error": type(exception).__name__,
        "message": str(exception),
        "details": {},
        "correlation_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat()
    }
