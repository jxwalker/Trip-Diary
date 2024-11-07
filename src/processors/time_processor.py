from datetime import datetime, timedelta
from typing import Tuple
from ..models.exceptions import TimeCalculationError

def calculate_checkin_time(departure_date: str, departure_time: str) -> Tuple[str, str]:
    """
    Calculate airport check-in time (2 hours before departure).
    
    Args:
        departure_date: Date in format 'YYYY-MM-DD'
        departure_time: Time in format 'HH:MM'
    
    Returns:
        Tuple of (checkin_date, checkin_time)
    
    Examples:
        >>> calculate_checkin_time('2024-12-20', '16:00')
        ('2024-12-20', '14:00')
        >>> calculate_checkin_time('2024-12-20', '01:00')
        ('2024-12-19', '23:00')
    """
    try:
        dep_datetime = datetime.strptime(f"{departure_date} {departure_time}", '%Y-%m-%d %H:%M')
        checkin_datetime = dep_datetime - timedelta(hours=2)
        return checkin_datetime.strftime('%Y-%m-%d'), checkin_datetime.strftime('%H:%M')
    except ValueError as e:
        raise TimeCalculationError(f"Could not calculate check-in time from {departure_date} {departure_time}: {str(e)}")