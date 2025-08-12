class ItineraryError(Exception):
    """Base class for itinerary-related errors."""
    pass

class PDFReadError(ItineraryError):
    """Raised when there's an error reading the PDF."""
    pass

class NoTravelContentError(ItineraryError):
    """Raised when no travel content is found in the document."""
    pass

class TimeCalculationError(ItineraryError):
    """Raised when there's an error calculating times."""
    pass