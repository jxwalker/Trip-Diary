"""
Enhanced Database Service
Implementation of StorageServiceInterface with improved functionality
"""
import json
import asyncio
import aiofiles
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from .interfaces import (
    StorageServiceInterface, 
    StorageResult, 
    QueryFilter, 
    QueryOptions,
    StorageType,
    QueryOperator,
    ServiceConfig
)
from ..models.database_models import (
    TripData, ProcessingState, ProcessingStatus, TripMetadata
)
from ..core.exceptions import DatabaseError, NotFoundError, ValidationError
from ..config import get_settings

logger = logging.getLogger(__name__)


class EnhancedDatabaseService(StorageServiceInterface):
    """Enhanced database service implementing the storage interface"""
    
    def __init__(self, config: Optional[ServiceConfig] = None):
        if config is None:
            settings = get_settings()
            config = ServiceConfig(
                enabled=True,
                timeout_seconds=30,
                cache_enabled=settings.database.cache_enabled,
                cache_ttl_seconds=settings.database.cache_ttl_seconds
            )
        
        super().__init__(config, logger)
        
        self.settings = get_settings()
        self.base_path = self.settings.database.get_database_path()
        self.trips_path = self.base_path / "trips"
        self.processing_path = self.base_path / "processing"
        self.metadata_path = self.base_path / "metadata"
        self.backups_path = self.settings.database.get_backup_path()
        
        # In-memory caches
        self._trip_cache: Dict[str, TripData] = {}
        self._processing_cache: Dict[str, ProcessingState] = {}
        self._metadata_cache: Dict[str, TripMetadata] = {}
        self._cache_loaded = False
    
    @property
    def storage_type(self) -> StorageType:
        """Get the storage backend type"""
        return StorageType.FILE
    
    async def initialize(self) -> None:
        """Initialize the database service"""
        try:
            # Create directories
            for path in [
                self.trips_path, self.processing_path, 
                self.metadata_path, self.backups_path
            ]:
                path.mkdir(parents=True, exist_ok=True)
            
            # Load caches
            await self._load_caches()
            
            logger.info(
                f"Enhanced database service initialized at {self.base_path}"
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize database service: {e}")
            raise DatabaseError(f"Database initialization failed: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            # Check if directories exist and are writable
            test_file = self.base_path / "health_check.tmp"
            async with aiofiles.open(test_file, 'w') as f:
                await f.write("health_check")
            test_file.unlink()
            
            stats = await self.get_storage_stats()
            
            return {
                "status": "healthy",
                "storage_type": self.storage_type.value,
                "base_path": str(self.base_path),
                "stats": stats,
                "cache_enabled": self.config.cache_enabled,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def cleanup(self) -> None:
        """Cleanup database resources"""
        # Clear caches
        self._trip_cache.clear()
        self._processing_cache.clear()
        self._metadata_cache.clear()
        self._cache_loaded = False

        logger.info("Database service cleanup completed")

    async def clear_trip_cache(self, trip_id: str) -> None:
        """Clear cache for a specific trip"""
        self._trip_cache.pop(trip_id, None)
        self._processing_cache.pop(trip_id, None)
        self._metadata_cache.pop(trip_id, None)
        logger.info(f"Cleared cache for trip {trip_id}")
    
    async def initialize_storage(self) -> StorageResult:
        """Initialize storage backend"""
        try:
            await self.initialize()
            return StorageResult.success_result(
                metadata={"message": "Storage initialized successfully"}
            )
        except Exception as e:
            return StorageResult.error_result(str(e))
    
    async def create_backup(
        self, backup_path: Optional[str] = None
    ) -> StorageResult:
        """Create a backup of the storage"""
        try:
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = str(
                    self.backups_path / f"backup_{timestamp}.json"
                )
            
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "trips": {},
                "processing_states": {},
                "metadata": {}
            }
            
            # Backup trips
            for trip_file in self.trips_path.glob("*.json"):
                async with aiofiles.open(trip_file, 'r') as f:
                    content = await f.read()
                    backup_data["trips"][trip_file.stem] = json.loads(content)
            
            # Backup processing states
            for proc_file in self.processing_path.glob("*.json"):
                async with aiofiles.open(proc_file, 'r') as f:
                    content = await f.read()
                    backup_data["processing_states"][proc_file.stem] = (
                        json.loads(content)
                    )
            
            # Save backup
            async with aiofiles.open(backup_path, 'w') as f:
                await f.write(json.dumps(backup_data, indent=2))
            
            return StorageResult.success_result(
                data={"backup_path": backup_path},
                metadata={"trip_count": len(backup_data["trips"])}
            )
            
        except Exception as e:
            return StorageResult.error_result(f"Backup failed: {e}")
    
    async def restore_backup(self, backup_path: str) -> StorageResult:
        """Restore from a backup"""
        try:
            async with aiofiles.open(backup_path, 'r') as f:
                content = await f.read()
                backup_data = json.loads(content)
            
            restored_count = 0
            
            # Restore trips
            for trip_id, trip_data in backup_data.get("trips", {}).items():
                trip_file = self.trips_path / f"{trip_id}.json"
                async with aiofiles.open(trip_file, 'w') as f:
                    await f.write(json.dumps(trip_data, indent=2))
                restored_count += 1
            
            # Restore processing states
            for proc_id, proc_data in backup_data.get(
                "processing_states", {}
            ).items():
                proc_file = self.processing_path / f"{proc_id}.json"
                async with aiofiles.open(proc_file, 'w') as f:
                    await f.write(json.dumps(proc_data, indent=2))
            
            # Reload caches
            await self._load_caches()
            
            return StorageResult.success_result(
                metadata={"restored_count": restored_count}
            )
            
        except Exception as e:
            return StorageResult.error_result(f"Restore failed: {e}")
    
    # Trip Data Operations
    async def save_trip_data(self, trip_data: TripData) -> StorageResult:
        """Save trip data"""
        try:
            trip_data.update_timestamp()
            
            # Save to file
            trip_file = self.trips_path / f"{trip_data.trip_id}.json"
            async with aiofiles.open(trip_file, 'w') as f:
                await f.write(json.dumps(trip_data.to_dict(), indent=2))
            
            # Update cache
            if self.config.cache_enabled:
                self._trip_cache[trip_data.trip_id] = trip_data
            
            # Update metadata
            metadata = TripMetadata.from_trip_data(trip_data)
            await self._save_metadata(metadata)
            
            return StorageResult.success_result(
                data={"trip_id": trip_data.trip_id}
            )
            
        except Exception as e:
            logger.error(f"Failed to save trip data {trip_data.trip_id}: {e}")
            return StorageResult.error_result(f"Save failed: {e}")
    
    async def save_enhanced_guide(
        self, trip_id: str, guide: Dict[str, Any]
    ) -> bool:
        """Save enhanced guide for a trip"""
        try:
            # Get existing trip data
            trip_data = await self.get_trip_data(trip_id)
            if not trip_data:
                logger.warning(f"Trip not found for saving guide: {trip_id}")
                return False
            
            # Update with enhanced guide
            trip_data.enhanced_guide = guide
            trip_data.updated_at = datetime.now().isoformat()
            
            # Save updated trip data
            result = await self.save_trip_data(trip_data)
            return result.success if result else False
        except Exception as e:
            logger.error(f"Failed to save enhanced guide for {trip_id}: {e}")
            return False

    async def get_trip_data(self, trip_id: str) -> Optional[TripData]:
        """Get trip data by ID"""
        try:
            # Check cache first
            if self.config.cache_enabled and trip_id in self._trip_cache:
                return self._trip_cache[trip_id]
            
            # Load from file
            trip_file = self.trips_path / f"{trip_id}.json"
            if not trip_file.exists():
                return None
            
            async with aiofiles.open(trip_file, 'r') as f:
                content = await f.read()
                data = json.loads(content)
                trip_data = TripData.from_dict(data)
            
            # Update cache
            if self.config.cache_enabled:
                self._trip_cache[trip_id] = trip_data
            
            return trip_data
            
        except Exception as e:
            logger.error(f"Failed to get trip data {trip_id}: {e}")
            return None
    
    async def update_trip_data(self, trip_id: str, **updates) -> StorageResult:
        """Update trip data"""
        try:
            trip_data = await self.get_trip_data(trip_id)
            if not trip_data:
                return StorageResult.error_result("Trip not found")
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(trip_data, key):
                    setattr(trip_data, key, value)
            
            # Save updated data
            return await self.save_trip_data(trip_data)
            
        except Exception as e:
            return StorageResult.error_result(f"Update failed: {e}")
    
    async def delete_trip_data(self, trip_id: str) -> StorageResult:
        """Delete trip data"""
        try:
            trip_file = self.trips_path / f"{trip_id}.json"
            if trip_file.exists():
                trip_file.unlink()
            
            # Remove from cache
            self._trip_cache.pop(trip_id, None)
            self._metadata_cache.pop(trip_id, None)
            
            # Delete metadata
            metadata_file = self.metadata_path / f"{trip_id}.json"
            if metadata_file.exists():
                metadata_file.unlink()
            
            return StorageResult.success_result()
            
        except Exception as e:
            return StorageResult.error_result(f"Delete failed: {e}")
    
    async def list_trips(
        self,
        user_id: Optional[str] = None,
        options: Optional[QueryOptions] = None
    ) -> List[TripMetadata]:
        """List trips with optional filtering"""
        try:
            await self._ensure_metadata_loaded()
            
            # Start with all trips
            trips = list(self._metadata_cache.values())
            
            # Filter by user_id
            if user_id:
                trips = [trip for trip in trips if trip.user_id == user_id]
            
            # Apply filters
            if options and options.filters:
                trips = self._apply_filters(trips, options.filters)
            
            # Apply sorting
            if options and options.sort_by:
                reverse = options.sort_desc
                trips.sort(
                    key=lambda x: getattr(x, options.sort_by, ""), 
                    reverse=reverse
                )
            
            # Apply pagination
            if options and options.offset:
                trips = trips[options.offset:]
            if options and options.limit:
                trips = trips[:options.limit]
            
            return trips
            
        except Exception as e:
            logger.error(f"Failed to list trips: {e}")
            return []
    
    async def search_trips(
        self,
        query: str,
        user_id: Optional[str] = None
    ) -> List[TripMetadata]:
        """Search trips by text query"""
        try:
            all_trips = await self.list_trips(user_id=user_id)
            query_lower = query.lower()
            
            matching_trips = []
            for trip in all_trips:
                # Search in destination, title, and tags
                searchable_text = (
                    f"{trip.destination} {trip.title} {' '.join(trip.tags)}"
                ).lower()
                if query_lower in searchable_text:
                    matching_trips.append(trip)
            
            return matching_trips
            
        except Exception as e:
            logger.error(f"Failed to search trips: {e}")
            return []
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            trip_count = len(list(self.trips_path.glob("*.json")))
            processing_count = len(list(self.processing_path.glob("*.json")))
            
            # Calculate total size
            total_size = sum(
                f.stat().st_size 
                for f in self.base_path.rglob("*.json")
                if f.is_file()
            )
            
            return {
                "trip_count": trip_count,
                "processing_count": processing_count,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "cache_enabled": self.config.cache_enabled,
                "cached_trips": len(self._trip_cache),
                "storage_type": self.storage_type.value
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {"error": str(e)}
    
    # Helper methods
    async def _load_caches(self):
        """Load data into caches"""
        if self._cache_loaded or not self.config.cache_enabled:
            return
        
        try:
            # Load trip metadata
            for metadata_file in self.metadata_path.glob("*.json"):
                async with aiofiles.open(metadata_file, 'r') as f:
                    content = await f.read()
                    data = json.loads(content)
                    metadata = TripMetadata.from_dict(data)
                    self._metadata_cache[metadata.trip_id] = metadata
            
            self._cache_loaded = True
            logger.info(
                f"Loaded {len(self._metadata_cache)} trip metadata into cache"
            )
            
        except Exception as e:
            logger.error(f"Failed to load caches: {e}")
    
    async def _ensure_metadata_loaded(self):
        """Ensure metadata is loaded"""
        if not self._cache_loaded:
            await self._load_caches()
    
    async def _save_metadata(self, metadata: TripMetadata):
        """Save trip metadata"""
        try:
            metadata_file = self.metadata_path / f"{metadata.trip_id}.json"
            async with aiofiles.open(metadata_file, 'w') as f:
                await f.write(json.dumps(metadata.to_dict(), indent=2))
            
            # Update cache
            if self.config.cache_enabled:
                self._metadata_cache[metadata.trip_id] = metadata
                
        except Exception as e:
            logger.error(
                f"Failed to save metadata for {metadata.trip_id}: {e}"
            )
    
    def _apply_filters(self, trips: List[TripMetadata], filters: List[QueryFilter]) -> List[TripMetadata]:
        """Apply query filters to trip list"""
        filtered_trips = trips
        
        for filter_obj in filters:
            field = filter_obj.field
            operator = filter_obj.operator
            value = filter_obj.value
            
            if operator == QueryOperator.EQUALS:
                filtered_trips = [t for t in filtered_trips if getattr(t, field, None) == value]
            elif operator == QueryOperator.CONTAINS:
                filtered_trips = [t for t in filtered_trips if value.lower() in str(getattr(t, field, "")).lower()]
            elif operator == QueryOperator.GREATER_THAN:
                filtered_trips = [t for t in filtered_trips if getattr(t, field, "") > value]
            elif operator == QueryOperator.LESS_THAN:
                filtered_trips = [t for t in filtered_trips if getattr(t, field, "") < value]
            # Add more operators as needed
        
        return filtered_trips
    
    # Processing State Operations
    async def create_processing_state(
        self,
        trip_id: str,
        message: str,
        progress: int = 0
    ) -> StorageResult:
        """Create a new processing state"""
        try:
            from datetime import datetime
            from ..models.database_models import ProcessingStatus
            now = datetime.utcnow()
            processing_state = ProcessingState(
                trip_id=trip_id,
                status=ProcessingStatus.PROCESSING,
                progress=progress,
                message=message,
                created_at=now,
                updated_at=now
            )
            
            # Save to file
            state_file = self.processing_path / f"{trip_id}.json"
            async with aiofiles.open(state_file, 'w') as f:
                await f.write(json.dumps(processing_state.to_dict(), indent=2))
            
            # Update cache
            if self.config.cache_enabled:
                self._processing_cache[trip_id] = processing_state
            
            return StorageResult.success_result(processing_state)
            
        except Exception as e:
            logger.error(f"Failed to create processing state for {trip_id}: {e}")
            return StorageResult.error_result(str(e))
    
    async def update_processing_state(
        self,
        trip_id: str,
        status: Optional[ProcessingStatus] = None,
        message: Optional[str] = None,
        progress: Optional[int] = None,
        **kwargs
    ) -> StorageResult:
        """Update an existing processing state"""
        try:
            # Get existing state
            state = await self.get_processing_state(trip_id)
            if not state:
                return StorageResult.error_result(f"Processing state not found for {trip_id}")
            
            # Update fields
            if status is not None:
                state.status = status
            if message is not None:
                state.message = message
            if progress is not None:
                state.progress = progress

            # Always update the timestamp
            from datetime import datetime
            state.updated_at = datetime.utcnow()
            
            # Save to file
            state_file = self.processing_path / f"{trip_id}.json"
            async with aiofiles.open(state_file, 'w') as f:
                await f.write(json.dumps(state.to_dict(), indent=2))
            
            # Update cache
            if self.config.cache_enabled:
                self._processing_cache[trip_id] = state
            
            return StorageResult.success_result(state)
            
        except Exception as e:
            logger.error(f"Failed to update processing state for {trip_id}: {e}")
            return StorageResult.error_result(str(e))
    
    async def get_processing_state(self, trip_id: str) -> Optional[ProcessingState]:
        """Get processing state by trip ID"""
        try:
            # Check cache first
            if self.config.cache_enabled and trip_id in self._processing_cache:
                return self._processing_cache[trip_id]
            
            # Load from file
            state_file = self.processing_path / f"{trip_id}.json"
            if not state_file.exists():
                return None
            
            async with aiofiles.open(state_file, 'r') as f:
                data = json.loads(await f.read())
                state = ProcessingState(**data)
            
            # Update cache
            if self.config.cache_enabled:
                self._processing_cache[trip_id] = state
            
            return state
            
        except Exception as e:
            logger.error(f"Failed to get processing state for {trip_id}: {e}")
            return None
    
    async def delete_processing_state(self, trip_id: str) -> StorageResult:
        """Delete processing state"""
        try:
            # Delete file
            state_file = self.processing_path / f"{trip_id}.json"
            if state_file.exists():
                state_file.unlink()
            
            # Remove from cache
            if trip_id in self._processing_cache:
                del self._processing_cache[trip_id]
            
            return StorageResult.success_result()
            
        except Exception as e:
            logger.error(f"Failed to delete processing state for {trip_id}: {e}")
            return StorageResult.error_result(str(e))
    
    async def cleanup_old_data(self, older_than_days: int = 30) -> StorageResult:
        """Clean up old data older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=older_than_days)
            deleted_count = 0
            
            # Clean up processing states
            for state_file in self.processing_path.glob("*.json"):
                if state_file.stat().st_mtime < cutoff_date.timestamp():
                    state_file.unlink()
                    deleted_count += 1
            
            # Clean up old trips
            for trip_file in self.trips_path.glob("*.json"):
                if trip_file.stat().st_mtime < cutoff_date.timestamp():
                    trip_file.unlink()
                    deleted_count += 1
            
            return StorageResult.success_result(
                data={"deleted_count": deleted_count},
                metadata={"cutoff_date": cutoff_date.isoformat()}
            )
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return StorageResult.error_result(str(e))
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> StorageResult:
        """Execute a custom query (for file-based storage, this is limited)"""
        try:
            # For file-based storage, we can only execute simple queries
            if query == "count_trips":
                count = len(list(self.trips_path.glob("*.json")))
                return StorageResult.success_result(data={"count": count})
            elif query == "count_processing":
                count = len(list(self.processing_path.glob("*.json")))
                return StorageResult.success_result(data={"count": count})
            else:
                return StorageResult.error_result("Unsupported query for file-based storage")
                
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            return StorageResult.error_result(str(e))
    
    async def update_preference_progress(
        self,
        trip_id: str,
        preferences_collected: bool = False,
        preferences_progress: int = 0
    ) -> StorageResult:
        """Update preference collection progress"""
        try:
            # Get trip data
            trip_data = await self.get_trip_data(trip_id)
            if not trip_data:
                return StorageResult.error_result(f"Trip {trip_id} not found")
            
            # Update preferences
            if not hasattr(trip_data, 'preferences_collected'):
                trip_data.preferences_collected = preferences_collected
            if not hasattr(trip_data, 'preferences_progress'):
                trip_data.preferences_progress = preferences_progress
            
            # Save updated trip data
            return await self.save_trip_data(trip_data)
            
        except Exception as e:
            logger.error(f"Failed to update preference progress for {trip_id}: {e}")
            return StorageResult.error_result(str(e))
    
    async def save_enhanced_guide_data(self, trip_id: str, guide_data: Dict[str, Any]) -> StorageResult:
        """Save enhanced guide data for a trip - renamed method to avoid caching issues"""
        logger.info(f"DEBUG: save_enhanced_guide_data called for trip {trip_id}")
        try:
            # Get trip data
            trip_data = await self.get_trip_data(trip_id)
            if not trip_data:
                return StorageResult.error_result(f"Trip {trip_id} not found")
            
            # Add enhanced guide data to trip
            trip_data.enhanced_guide = guide_data
            trip_data.enhanced_guide_created_at = datetime.utcnow()
            
            # Save updated trip data
            return await self.save_trip_data(trip_data)
            
        except Exception as e:
            logger.error(f"Failed to save enhanced guide for {trip_id}: {e}")
            return StorageResult.error_result(str(e))
    
    async def get_enhanced_guide(self, trip_id: str) -> Optional[Dict[str, Any]]:
        """Get enhanced guide data for a trip"""
        try:
            trip_data = await self.get_trip_data(trip_id)
            if not trip_data:
                return None
            
            return getattr(trip_data, 'enhanced_guide', None)
            
        except Exception as e:
            logger.error(f"Failed to get enhanced guide for {trip_id}: {e}")
            return None
