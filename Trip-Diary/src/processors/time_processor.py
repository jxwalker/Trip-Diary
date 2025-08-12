from datetime import datetime, timedelta
from typing import Tuple
from ..models.exceptions import TimeCalculationError

def calculate_checkin_time(departure_date: str, departure_time: str, hours_before: int = 2) -> Tuple[str, str]:
    """
    Calculate airport check-in time (default 2 hours before departure).
    
    Args:
        departure_date: Date in format 'YYYY-MM-DD'
        departure_time: Time in format 'HH:MM'
        hours_before: Hours before departure for check-in
    
    Returns:
        Tuple of (checkin_date, checkin_time) in same formats
    
    Raises:
        TimeCalculationError: If date/time parsing fails
    """
    try:
        dep_datetime = datetime.strptime(f"{departure_date} {departure_time}", '%Y-%m-%d %H:%M')
        checkin_datetime = dep_datetime - timedelta(hours=hours_before)
        return (
            checkin_datetime.strftime('%Y-%m-%d'),
            checkin_datetime.strftime('%H:%M')
        )
    except ValueError as e:
        raise TimeCalculationError(
            f"Could not calculate check-in time from {departure_date} {departure_time}: {str(e)}"
        )