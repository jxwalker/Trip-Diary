"""
TripCraft AI API - Main application entry point
"""
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.api.app_factory import create_app

# Create the FastAPI application using the factory pattern
app = create_app()

# The app is now fully configured through the factory pattern
# All routes, middleware, and services are configured in the modular structure

if __name__ == "__main__":
    import uvicorn
    from config import config
    uvicorn.run(app, host=config.HOST, port=config.PORT)

