"""
Comprehensive Database Service for Trip Diary
Handles both persistent storage and active processing state
Replaces in-memory dictionaries with proper database persistence
"""

import json
import uuid
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import aiofiles
import logging
from dataclasses import dataclass, asdict
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from config import config

logger = logging.getLogger(__name__)

class ProcessingStatus(Enum):
    """Processing status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"

@dataclass
class ProcessingState:
    """Processing state for active trips"""
    trip_id: str
    status: ProcessingStatus
    progress: int
    message: str
    created_at: str
    updated_at: str
    extracted_data: Optional[Dict] = None
    error_details: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API responses"""
        return {
            "trip_id": self.trip_id,
            "status": self.status.value,
            "progress": self.progress,
            "message": self.message,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "extracted_data": self.extracted_data,
            "error_details": self.error_details
        }

@dataclass
class TripData:
    """Complete trip data structure"""
    trip_id: str
    extracted_data: Optional[Dict] = None
    itinerary: Optional[Dict] = None
    recommendations: Optional[Dict] = None
    enhanced_guide: Optional[Dict] = None
    preferences: Optional[Dict] = None
    preferences_raw: Optional[Dict] = None
    preference_progress: Optional[Dict] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    user_id: str = "default"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)

class DatabaseService:
    """
    Comprehensive database service that handles:
    1. Processing state (replaces processing_status dict)
    2. Trip data (replaces trip_data dict)
    3. Persistent storage
    4. Cleanup and maintenance
    """
    
    def __init__(self, base_path: Optional[str] = None):
        if base_path is None:
            base_path = Path(__file__).parent.parent / "data"
        
        self.base_path = Path(base_path)
        self.processing_path = self.base_path / "processing"
        self.trips_path = self.base_path / "trips"
        self.index_path = self.base_path / "index"
        
        # Create directories
        for path in [self.processing_path, self.trips_path, self.index_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # In-memory caches for performance
        self._processing_cache: Dict[str, ProcessingState] = {}
        self._trip_cache: Dict[str, TripData] = {}
        self._cache_loaded = False
        
        logger.info(f"Database service initialized at {self.base_path}")
    
    async def _ensure_cache_loaded(self):
        """Ensure caches are loaded from disk"""
        if not self._cache_loaded:
            await self._load_caches()
            self._cache_loaded = True
    
    async def _load_caches(self):
        """Load caches from disk"""
        try:
            # Load processing states
            for file_path in self.processing_path.glob("*.json"):
                try:
                    async with aiofiles.open(file_path, 'r') as f:
                        data = json.loads(await f.read())
                        state = ProcessingState(**data)
                        self._processing_cache[state.trip_id] = state
                except Exception as e:
                    logger.warning(f"Failed to load processing state from {file_path}: {e}")

            # Load recent trip data (last 100 trips for cache)
            trip_files = sorted(
                self.trips_path.glob("*.json"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )[:100]

            for file_path in trip_files:
                try:
                    async with aiofiles.open(file_path, 'r') as f:
                        data = json.loads(await f.read())

                        # Handle legacy data format
                        if "trip_id" in data:
                            # Filter out unknown fields for TripData
                            valid_fields = {
                                'trip_id', 'extracted_data', 'itinerary', 'recommendations',
                                'enhanced_guide', 'preferences', 'created_at', 'updated_at', 'user_id'
                            }
                            filtered_data = {k: v for k, v in data.items() if k in valid_fields}

                            # Set defaults for missing fields
                            if 'user_id' not in filtered_data:
                                filtered_data['user_id'] = 'default'

                            trip_data = TripData(**filtered_data)
                            self._trip_cache[trip_data.trip_id] = trip_data
                        else:
                            logger.debug(f"Skipping legacy file format: {file_path}")

                except Exception as e:
                    logger.debug(f"Skipping incompatible trip data from {file_path}: {e}")

            logger.info(f"Loaded {len(self._processing_cache)} processing states and {len(self._trip_cache)} trips into cache")

        except Exception as e:
            logger.error(f"Failed to load caches: {e}")
    
    # Processing State Management (replaces processing_status dict)
    
    async def create_processing_state(self, trip_id: str, message: str = "Starting processing...") -> ProcessingState:
        """Create a new processing state"""
        await self._ensure_cache_loaded()
        
        now = datetime.now().isoformat()
        state = ProcessingState(
            trip_id=trip_id,
            status=ProcessingStatus.PROCESSING,
            progress=0,
            message=message,
            created_at=now,
            updated_at=now
        )
        
        # Save to cache and disk
        self._processing_cache[trip_id] = state
        await self._save_processing_state(state)
        
        logger.info(f"Created processing state for trip {trip_id}")
        return state
    
    async def update_processing_state(
        self,
        trip_id: str,
        status: Optional[ProcessingStatus] = None,
        progress: Optional[int] = None,
        message: Optional[str] = None,
        extracted_data: Optional[Dict] = None,
        error_details: Optional[str] = None
    ) -> Optional[ProcessingState]:
        """Update processing state"""
        await self._ensure_cache_loaded()
        
        state = self._processing_cache.get(trip_id)
        if not state:
            logger.warning(f"Processing state not found for trip {trip_id}")
            return None
        
        # Update fields
        if status is not None:
            state.status = status
        if progress is not None:
            state.progress = progress
        if message is not None:
            state.message = message
        if extracted_data is not None:
            state.extracted_data = extracted_data
        if error_details is not None:
            state.error_details = error_details
        
        state.updated_at = datetime.now().isoformat()
        
        # Save to disk
        await self._save_processing_state(state)
        
        logger.debug(f"Updated processing state for trip {trip_id}: {state.status} ({state.progress}%)")
        return state
    
    async def get_processing_state(self, trip_id: str) -> Optional[ProcessingState]:
        """Get processing state"""
        await self._ensure_cache_loaded()
        
        state = self._processing_cache.get(trip_id)
        if not state:
            # Try to load from disk
            state = await self._load_processing_state(trip_id)
            if state:
                self._processing_cache[trip_id] = state
        
        return state
    
    async def update_preference_progress(
        self, 
        trip_id: str, 
        status: str = "processing",
        message: str = "",
        progress: int = 0
    ) -> bool:
        """Update preference generation progress in trip data"""
        trip_data = await self.get_trip_data(trip_id)
        if not trip_data:
            logger.warning(f"Trip {trip_id} not found for preference progress update")
            return False
        
        # Update preference progress in trip data
        if not hasattr(trip_data, 'preference_progress'):
            trip_data.preference_progress = {}
        
        trip_data.preference_progress = {
            "status": status,
            "message": message,
            "progress": progress,
            "updated_at": datetime.now().isoformat()
        }
        
        # Save updated trip data
        await self.update_trip_data(trip_id, **trip_data.to_dict())
        return True
    
    async def delete_processing_state(self, trip_id: str) -> bool:
        """Delete processing state (cleanup after completion)"""
        await self._ensure_cache_loaded()
        
        # Remove from cache
        if trip_id in self._processing_cache:
            del self._processing_cache[trip_id]
        
        # Remove from disk
        file_path = self.processing_path / f"{trip_id}.json"
        if file_path.exists():
            file_path.unlink()
            logger.debug(f"Deleted processing state for trip {trip_id}")
            return True
        
        return False
    
    async def _save_processing_state(self, state: ProcessingState):
        """Save processing state to disk"""
        file_path = self.processing_path / f"{state.trip_id}.json"
        data = asdict(state)
        # Convert enum to string for JSON serialization
        if hasattr(state.status, 'value'):
            data['status'] = state.status.value
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(json.dumps(data, indent=2, default=str))
    
    async def _load_processing_state(self, trip_id: str) -> Optional[ProcessingState]:
        """Load processing state from disk"""
        file_path = self.processing_path / f"{trip_id}.json"
        if not file_path.exists():
            return None
        
        try:
            async with aiofiles.open(file_path, 'r') as f:
                data = json.loads(await f.read())
                # Convert status string to enum if needed
                if 'status' in data and isinstance(data['status'], str):
                    data['status'] = ProcessingStatus(data['status'])
                return ProcessingState(**data)
        except Exception as e:
            logger.error(f"Failed to load processing state for {trip_id}: {e}")
            return None

    # Trip Data Management (replaces trip_data dict)
    
    async def save_enhanced_guide(self, trip_id: str, guide: Dict[str, Any]) -> bool:
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
            return await self.save_trip_data(trip_data)
        except Exception as e:
            logger.error(f"Failed to save enhanced guide for {trip_id}: {e}")
            return False

    async def save_trip_data(self, trip_data: TripData) -> bool:
        """Save trip data"""
        await self._ensure_cache_loaded()

        # Update timestamp
        trip_data.updated_at = datetime.now().isoformat()
        if not trip_data.created_at:
            trip_data.created_at = trip_data.updated_at

        # Save to cache
        self._trip_cache[trip_data.trip_id] = trip_data

        # Save to disk
        try:
            file_path = self.trips_path / f"{trip_data.trip_id}.json"
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(trip_data.to_dict(), indent=2, default=str))

            logger.info(f"Saved trip data for {trip_data.trip_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save trip data for {trip_data.trip_id}: {e}")
            return False

    async def get_trip_data(self, trip_id: str) -> Optional[TripData]:
        """Get trip data"""
        await self._ensure_cache_loaded()

        # Check cache first
        trip_data = self._trip_cache.get(trip_id)
        if trip_data:
            return trip_data

        # Load from disk
        try:
            file_path = self.trips_path / f"{trip_id}.json"
            if not file_path.exists():
                return None

            async with aiofiles.open(file_path, 'r') as f:
                data = json.loads(await f.read())
                trip_data = TripData(**data)

                # Add to cache
                self._trip_cache[trip_id] = trip_data
                return trip_data

        except Exception as e:
            logger.error(f"Failed to load trip data for {trip_id}: {e}")
            return None

    async def update_trip_data(
        self,
        trip_id: str,
        extracted_data: Optional[Dict] = None,
        itinerary: Optional[Dict] = None,
        recommendations: Optional[Dict] = None,
        enhanced_guide: Optional[Dict] = None,
        preferences: Optional[Dict] = None
    ) -> bool:
        """Update specific parts of trip data"""
        trip_data = await self.get_trip_data(trip_id)
        if not trip_data:
            # Create new trip data
            trip_data = TripData(trip_id=trip_id)

        # Update fields
        if extracted_data is not None:
            trip_data.extracted_data = extracted_data
        if itinerary is not None:
            trip_data.itinerary = itinerary
        if recommendations is not None:
            trip_data.recommendations = recommendations
        if enhanced_guide is not None:
            trip_data.enhanced_guide = enhanced_guide
        if preferences is not None:
            trip_data.preferences = preferences

        return await self.save_trip_data(trip_data)

    async def delete_trip_data(self, trip_id: str) -> bool:
        """Delete trip data"""
        await self._ensure_cache_loaded()

        # Remove from cache
        if trip_id in self._trip_cache:
            del self._trip_cache[trip_id]

        # Remove from disk
        file_path = self.trips_path / f"{trip_id}.json"
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted trip data for {trip_id}")
            return True

        return False

    async def list_trips(self, user_id: str = "default", limit: int = 50) -> List[Dict]:
        """List trips for a user"""
        await self._ensure_cache_loaded()

        trips = []

        # Get all trip files
        trip_files = list(self.trips_path.glob("*.json"))

        # Sort by modification time (newest first)
        trip_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        for file_path in trip_files[:limit]:
            try:
                async with aiofiles.open(file_path, 'r') as f:
                    data = json.loads(await f.read())

                    # Filter by user_id
                    if data.get("user_id", "default") != user_id:
                        continue

                    # Create summary
                    itinerary = data.get("itinerary", {})
                    trip_summary = itinerary.get("trip_summary", {})

                    trip_info = {
                        "trip_id": data["trip_id"],
                        "destination": trip_summary.get("destination", "Unknown"),
                        "start_date": trip_summary.get("start_date", ""),
                        "end_date": trip_summary.get("end_date", ""),
                        "created_at": data.get("created_at", ""),
                        "updated_at": data.get("updated_at", ""),
                        "has_enhanced_guide": "enhanced_guide" in data,
                        "flights": len(itinerary.get("flights", [])),
                        "hotels": len(itinerary.get("accommodations", []))
                    }
                    trips.append(trip_info)

            except Exception as e:
                logger.warning(f"Failed to process trip file {file_path}: {e}")

        return trips

    # Cleanup and Maintenance

    async def cleanup_old_processing_states(self, max_age_hours: int = 24) -> int:
        """Clean up old processing states"""
        await self._ensure_cache_loaded()

        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        cleaned_count = 0

        # Check cached states
        to_remove = []
        for trip_id, state in self._processing_cache.items():
            try:
                updated_at = datetime.fromisoformat(state.updated_at)
                if updated_at < cutoff_time:
                    to_remove.append(trip_id)
            except Exception:
                # Invalid timestamp, remove it
                to_remove.append(trip_id)

        # Remove old states
        for trip_id in to_remove:
            await self.delete_processing_state(trip_id)
            cleaned_count += 1

        # Check disk files
        for file_path in self.processing_path.glob("*.json"):
            try:
                if datetime.fromtimestamp(file_path.stat().st_mtime) < cutoff_time:
                    file_path.unlink()
                    cleaned_count += 1
            except Exception as e:
                logger.warning(f"Failed to check/remove old processing file {file_path}: {e}")

        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} old processing states")

        return cleaned_count

    async def get_database_stats(self) -> Dict:
        """Get database statistics"""
        await self._ensure_cache_loaded()

        # Count files
        processing_files = len(list(self.processing_path.glob("*.json")))
        trip_files = len(list(self.trips_path.glob("*.json")))

        # Calculate storage size
        total_size = 0
        for path in [self.processing_path, self.trips_path]:
            for file_path in path.rglob("*.json"):
                total_size += file_path.stat().st_size

        # Processing status breakdown
        status_counts = {}
        for state in self._processing_cache.values():
            status = state.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "processing_states": {
                "active": len(self._processing_cache),
                "on_disk": processing_files,
                "status_breakdown": status_counts
            },
            "trips": {
                "cached": len(self._trip_cache),
                "on_disk": trip_files
            },
            "storage": {
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "base_path": str(self.base_path)
            }
        }

# Global database service instance
db_service = DatabaseService()
