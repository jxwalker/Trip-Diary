import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logging(log_dir: str = "logs", debug: bool = False) -> None:
    """Configure logging for the application."""
    # Create logs directory if it doesn't exist
    Path(log_dir).mkdir(exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = Path(log_dir) / f"trip_diary_{timestamp}.log"
    
    # Set up logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler - all messages
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # Console handler - info and above
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if debug else logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Log initial message
    root_logger.info(f"Logging initialized. Log file: {log_file}")
    if debug:
        root_logger.debug("Debug logging enabled")

def log_gpt_response(
    logger: logging.Logger, response: str, cleaned: str
) -> None:
    """Log original and cleaned GPT response for debugging."""
    logger.debug("Original GPT response:")
    logger.debug(response)
    logger.debug("\nCleaned JSON:")
    logger.debug(cleaned)
