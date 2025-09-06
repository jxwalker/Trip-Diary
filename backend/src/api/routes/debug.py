"""
Debug route for testing service injection
"""
from fastapi import APIRouter
from ..dependencies.services import DatabaseServiceDep

router = APIRouter(prefix="/api", tags=["debug"])

@router.get("/debug/database-service")
async def debug_database_service(database_service: DatabaseServiceDep):
    """Debug endpoint to check database service"""
    return {
        "service_type": type(database_service).__name__,
        "service_module": type(database_service).__module__,
        "has_save_enhanced_guide": hasattr(database_service, 'save_enhanced_guide'),
        "methods": [attr for attr in dir(database_service) if not attr.startswith('_')],
        "save_methods": [attr for attr in dir(database_service) if 'save' in attr.lower()]
    }
