"""
Storage Service Interface
Standardized interface for data persistence services
"""
from abc import abstractmethod
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from .base import BaseService, ServiceConfig
from ...models.database_models import TripData, ProcessingState, TripMetadata


class StorageType(str, Enum):
    """Storage backend types"""
    FILE = "file"
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MEMORY = "memory"


class QueryOperator(str, Enum):
    """Query operators for filtering"""
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    IN = "in"


@dataclass
class QueryFilter:
    """Query filter for storage operations"""
    field: str
    operator: QueryOperator
    value: Any
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "field": self.field,
            "operator": self.operator.value,
            "value": self.value
        }


@dataclass
class QueryOptions:
    """Query options for storage operations"""
    filters: List[QueryFilter] = None
    sort_by: Optional[str] = None
    sort_desc: bool = False
    limit: Optional[int] = None
    offset: Optional[int] = None
    
    def __post_init__(self):
        if self.filters is None:
            self.filters = []


@dataclass
class StorageResult:
    """Result from storage operations"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def success_result(cls, data: Any = None, metadata: Dict[str, Any] = None):
        return cls(success=True, data=data, metadata=metadata)
    
    @classmethod
    def error_result(cls, error: str, metadata: Dict[str, Any] = None):
        return cls(success=False, error=error, metadata=metadata)


class StorageServiceInterface(BaseService):
    """Interface for storage services"""
    
    @property
    @abstractmethod
    def storage_type(self) -> StorageType:
        """Get the storage backend type"""
        pass
    
    @abstractmethod
    async def initialize_storage(self) -> StorageResult:
        """Initialize storage backend"""
        pass
    
    @abstractmethod
    async def create_backup(
        self, backup_path: Optional[str] = None
    ) -> StorageResult:
        """Create a backup of the storage"""
        pass
    
    @abstractmethod
    async def restore_backup(self, backup_path: str) -> StorageResult:
        """Restore from a backup"""
        pass
    
    # Trip Data Operations
    @abstractmethod
    async def save_trip_data(self, trip_data: TripData) -> StorageResult:
        """Save trip data"""
        pass
    
    @abstractmethod
    async def get_trip_data(self, trip_id: str) -> Optional[TripData]:
        """Get trip data by ID"""
        pass
    
    @abstractmethod
    async def update_trip_data(self, trip_id: str, **updates) -> StorageResult:
        """Update trip data"""
        pass
    
    @abstractmethod
    async def delete_trip_data(self, trip_id: str) -> StorageResult:
        """Delete trip data"""
        pass
    
    @abstractmethod
    async def list_trips(
        self,
        user_id: Optional[str] = None,
        options: Optional[QueryOptions] = None
    ) -> List[TripMetadata]:
        """List trips with optional filtering"""
        pass
    
    @abstractmethod
    async def search_trips(
        self,
        query: str,
        user_id: Optional[str] = None
    ) -> List[TripMetadata]:
        """Search trips by text query"""
        pass
    
    # Processing State Operations
    @abstractmethod
    async def create_processing_state(
        self,
        trip_id: str,
        message: str,
        progress: int = 0
    ) -> StorageResult:
        """Create processing state"""
        pass
    
    @abstractmethod
    async def get_processing_state(
        self, trip_id: str
    ) -> Optional[ProcessingState]:
        """Get processing state"""
        pass
    
    @abstractmethod
    async def update_processing_state(
        self,
        trip_id: str,
        status: Optional[str] = None,
        progress: Optional[int] = None,
        message: Optional[str] = None,
        **kwargs
    ) -> StorageResult:
        """Update processing state"""
        pass
    
    @abstractmethod
    async def delete_processing_state(self, trip_id: str) -> StorageResult:
        """Delete processing state"""
        pass
    
    # Preference Progress Operations
    @abstractmethod
    async def update_preference_progress(
        self,
        trip_id: str,
        status: str,
        message: str,
        progress: int
    ) -> StorageResult:
        """Update preference processing progress"""
        pass
    
    # Generic Operations
    @abstractmethod
    async def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> StorageResult:
        """Execute raw query (for advanced operations)"""
        pass
    
    @abstractmethod
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        pass
    
    @abstractmethod
    async def cleanup_old_data(
        self, older_than_days: int = 30
    ) -> StorageResult:
        """Clean up old data"""
        pass
    
    # Utility Methods
    def build_filter(
        self,
        field: str,
        operator: Union[QueryOperator, str],
        value: Any
    ) -> QueryFilter:
        """Build a query filter"""
        if isinstance(operator, str):
            operator = QueryOperator(operator)
        return QueryFilter(field=field, operator=operator, value=value)
    
    def build_query_options(
        self,
        filters: Optional[List[QueryFilter]] = None,
        sort_by: Optional[str] = None,
        sort_desc: bool = False,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> QueryOptions:
        """Build query options"""
        return QueryOptions(
            filters=filters or [],
            sort_by=sort_by,
            sort_desc=sort_desc,
            limit=limit,
            offset=offset
        )
    
    async def get_trip_count(self, user_id: Optional[str] = None) -> int:
        """Get total trip count"""
        trips = await self.list_trips(user_id=user_id)
        return len(trips)
    
    async def get_recent_trips(
        self,
        user_id: Optional[str] = None,
        limit: int = 10
    ) -> List[TripMetadata]:
        """Get recent trips"""
        options = self.build_query_options(
            sort_by="created_at",
            sort_desc=True,
            limit=limit
        )
        return await self.list_trips(user_id=user_id, options=options)
    
    async def trip_exists(self, trip_id: str) -> bool:
        """Check if trip exists"""
        trip_data = await self.get_trip_data(trip_id)
        return trip_data is not None
    
    async def get_trips_by_destination(
        self,
        destination: str,
        user_id: Optional[str] = None
    ) -> List[TripMetadata]:
        """Get trips by destination"""
        filter_dest = self.build_filter(
            "destination", QueryOperator.CONTAINS, destination
        )
        options = self.build_query_options(filters=[filter_dest])
        return await self.list_trips(user_id=user_id, options=options)
    
    async def get_trips_by_date_range(
        self,
        start_date: str,
        end_date: str,
        user_id: Optional[str] = None
    ) -> List[TripMetadata]:
        """Get trips within date range"""
        filters = [
            self.build_filter(
                "start_date", QueryOperator.GREATER_THAN, start_date
            ),
            self.build_filter("end_date", QueryOperator.LESS_THAN, end_date)
        ]
        options = self.build_query_options(filters=filters)
        return await self.list_trips(user_id=user_id, options=options)
