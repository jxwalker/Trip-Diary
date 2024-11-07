from time import perf_counter
from functools import wraps
from typing import Dict, Any
from contextlib import contextmanager

class Timer:
    """Utility class for tracking execution times."""
    
    _timings: Dict[str, float] = {}
    
    @classmethod
    @contextmanager
    def track(cls, name: str):
        """Context manager for tracking execution time of a block of code."""
        start = perf_counter()
        yield
        end = perf_counter()
        cls._timings[name] = end - start
    
    @classmethod
    def get_timings(cls) -> Dict[str, float]:
        """Get all recorded timings."""
        return cls._timings
    
    @classmethod
    def clear_timings(cls):
        """Clear all recorded timings."""
        cls._timings.clear()
    
    @classmethod
    def format_timings(cls) -> str:
        """Format all timings as a string."""
        if not cls._timings:
            return ""
        
        lines = ["Performance Metrics:"]
        for name, duration in cls._timings.items():
            lines.append(f"  {name}: {duration:.3f}s")
        return "\n".join(lines)
