"""
Input validation utilities for consistent data validation across services
"""
import re
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from .error_handling import ValidationError


def validate_required_field(value: Any, field_name: str) -> Any:
    """
    Validate that a required field is not None or empty

    Args:
        value: Value to validate
        field_name: Name of the field for error messages

    Returns:
        The validated value

    Raises:
        ValidationError: If value is None or empty
    """
    if value is None:
        raise ValidationError(f"{field_name} is required")

    if isinstance(value, str) and not value.strip():
        raise ValidationError(f"{field_name} cannot be empty")

    return value


def validate_file_path(file_path: str, must_exist: bool = True) -> Path:
    """
    Validate file path

    Args:
        file_path: Path to validate
        must_exist: Whether file must exist

    Returns:
        Validated Path object

    Raises:
        ValidationError: If path is invalid
    """
    if not file_path:
        raise ValidationError("File path cannot be empty")

    path_obj = Path(file_path)

    if must_exist and not path_obj.exists():
        raise ValidationError(f"File does not exist: {file_path}")

    return path_obj


def validate_pdf_file(file_path: str) -> Path:
    """
    Validate PDF file path

    Args:
        file_path: Path to PDF file

    Returns:
        Validated Path object

    Raises:
        ValidationError: If not a valid PDF file
    """
    path_obj = validate_file_path(file_path, must_exist=True)

    if path_obj.suffix.lower() != '.pdf':
        raise ValidationError(f"File must be a PDF: {file_path}")

    return path_obj


def validate_trip_id(trip_id: str) -> str:
    """
    Validate trip ID format

    Args:
        trip_id: Trip ID to validate

    Returns:
        Validated trip ID

    Raises:
        ValidationError: If trip ID is invalid
    """
    if not trip_id:
        raise ValidationError("Trip ID cannot be empty")

    if not isinstance(trip_id, str):
        raise ValidationError("Trip ID must be a string")

    # Basic validation - alphanumeric with hyphens/underscores
    if not re.match(r'^[a-zA-Z0-9_-]+$', trip_id):
        raise ValidationError("Trip ID contains invalid characters")

    if len(trip_id) < 3 or len(trip_id) > 50:
        raise ValidationError("Trip ID must be between 3 and 50 characters")

    return trip_id


def validate_date_string(date_str: str, field_name: str = "date") -> str:
    """
    Validate date string in YYYY-MM-DD format

    Args:
        date_str: Date string to validate
        field_name: Name of the field for error messages

    Returns:
        Validated date string

    Raises:
        ValidationError: If date string is invalid
    """
    if not date_str:
        raise ValidationError(f"{field_name} cannot be empty")

    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        raise ValidationError(f"{field_name} must be in YYYY-MM-DD format")


def validate_destination(destination: str) -> str:
    """
    Validate destination string

    Args:
        destination: Destination to validate

    Returns:
        Validated destination

    Raises:
        ValidationError: If destination is invalid
    """
    if not destination:
        raise ValidationError("Destination cannot be empty")

    if not isinstance(destination, str):
        raise ValidationError("Destination must be a string")

    destination = destination.strip()

    if len(destination) < 2:
        raise ValidationError("Destination must be at least 2 characters")

    if len(destination) > 200:
        raise ValidationError("Destination must be less than 200 characters")

    return destination
