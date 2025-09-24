"""
Standardized error handling utilities
"""
import logging
import traceback
from typing import Dict, Any, Optional, Union
from functools import wraps


class TripDiaryError(Exception):
    """Base exception for Trip Diary application"""
    pass


class ConfigurationError(TripDiaryError):
    """Raised when configuration is invalid"""
    pass


class APIError(TripDiaryError):
    """Raised when external API calls fail"""
    pass


class ProcessingError(TripDiaryError):
    """Raised when document processing fails"""
    pass


class ValidationError(TripDiaryError):
    """Raised when input validation fails"""
    pass


def safe_execute(
    operation: str,
    logger: Optional[logging.Logger] = None,
    default_return: Any = None,
    raise_on_error: bool = False
):
    """
    Decorator for safe execution with consistent error handling

    Args:
        operation: Description of the operation for logging
        logger: Logger instance to use
        default_return: Value to return on error
        raise_on_error: Whether to re-raise exceptions
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                return _handle_error(
                    e, operation, logger, default_return, raise_on_error
                )

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return _handle_error(
                    e, operation, logger, default_return, raise_on_error
                )

        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def _handle_error(
    error: Exception,
    operation: str,
    logger: Optional[logging.Logger],
    default_return: Any,
    raise_on_error: bool
) -> Any:
    """Internal error handling logic"""
    error_msg = f"Error in {operation}: {str(error)}"

    if logger:
        logger.error(error_msg)
        logger.debug(traceback.format_exc())
    else:
        print(f"ERROR: {error_msg}")

    if raise_on_error:
        raise error

    return default_return


def create_error_response(
    error: Union[str, Exception],
    operation: str = "operation",
    include_traceback: bool = False
) -> Dict[str, Any]:
    """
    Create standardized error response

    Args:
        error: Error message or exception
        operation: Operation that failed
        include_traceback: Whether to include traceback in response

    Returns:
        Standardized error response dictionary
    """
    error_msg = str(error)

    response = {
        "success": False,
        "error": error_msg,
        "operation": operation,
        "timestamp": None
    }

    if include_traceback and isinstance(error, Exception):
        response["traceback"] = traceback.format_exc()

    return response


def log_and_return_error(
    logger: logging.Logger,
    error: Exception,
    operation: str,
    default_return: Any = None
) -> Any:
    """
    Log error and return default value

    Args:
        logger: Logger instance
        error: Exception that occurred
        operation: Description of failed operation
        default_return: Value to return

    Returns:
        default_return value
    """
    logger.error(f"Error in {operation}: {str(error)}")
    logger.debug(traceback.format_exc())
    return default_return
