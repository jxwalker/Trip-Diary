"""
Enhanced Trip Storage Service
Improved trip data management with better organization and retrieval
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import aiofiles
import asyncio
from dataclasses import dataclass, asdict

@dataclass
class TripMetadata:
    """Trip metadata for quick access without loading full trip data"""
    trip_id: str
    destination: str
    start_date: str
    end_date: str
    created_at: str
    updated_at: str
    status: str  # "processing", "completed", "error"
    profile_id: Optional[str] = None
    travelers: List[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.travelers is None:
            self.travelers = []
        if self.tags is None:
            self.tags = []

class TripStorageService:
    """
    Manages trip data storage with improved organization:
    - Separate metadata for quick listing
    - Full trip data stored separately
    - Profile associations
    - Better search and filtering
    """
    
    def __init__(self, base_path: str = "data/trips"):
        self.base_path = Path(base_path)
        self.metadata_path = self.base_path / "metadata"
        self.data_path = self.base_path / "data"
        self.uploads_path = self.base_path / "uploads"
        
        # Create directories
        self.metadata_path.mkdir(parents=True, exist_ok=True)
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.uploads_path.mkdir(parents=True, exist_ok=True)
        
        # Cache for metadata
        self._metadata_cache: Dict[str, TripMetadata] = {}
        self._load_metadata_cache()
    
    def _load_metadata_cache(self):
        """Load all metadata into cache for quick access"""
        try:
            for file in self.metadata_path.glob("*.json"):
                with open(file, 'r') as f:
                    data = json.load(f)
                    self._metadata_cache[data["trip_id"]] = TripMetadata(
                        **data)
        except Exception as e:
            print(f"Error loading metadata cache: {e}")
    
    async def create_trip(self, initial_data: Dict) -> str:
        """Create a new trip with initial data"""
        trip_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Extract metadata
        metadata = TripMetadata(
            trip_id=trip_id,
            destination=initial_data.get("destination", "Unknown"),
            start_date=initial_data.get("start_date", ""),
            end_date=initial_data.get("end_date", ""),
            created_at=timestamp,
            updated_at=timestamp,
            status="processing",
            profile_id=initial_data.get("profile_id"),
            travelers=initial_data.get("travelers", []),
            tags=initial_data.get("tags", [])
        )
        
        # Save metadata
        await self.save_metadata(metadata)
        
        # Save full trip data
        trip_data = {
            "trip_id": trip_id,
            "metadata": asdict(metadata),
            "extracted_data": initial_data.get("extracted_data", {}),
            "preferences": initial_data.get("preferences", {}),
            "itinerary": initial_data.get("itinerary", {}),
            "enhanced_guide": initial_data.get("enhanced_guide", {}),
            "uploads": initial_data.get("uploads", [])
        }
        
        await self.save_trip_data(trip_id, trip_data)
        
        return trip_id
    
    async def save_metadata(self, metadata: TripMetadata):
        """Save trip metadata"""
        metadata_file = self.metadata_path / f"{metadata.trip_id}.json"
        
        async with aiofiles.open(metadata_file, 'w') as f:
            await f.write(json.dumps(asdict(metadata), indent=2))
        
        # Update cache
        self._metadata_cache[metadata.trip_id] = metadata
    
    async def save_trip_data(self, trip_id: str, data: Dict):
        """Save full trip data"""
        data_file = self.data_path / f"{trip_id}.json"
        
        # Update timestamp
        data["metadata"]["updated_at"] = datetime.now().isoformat()
        
        async with aiofiles.open(data_file, 'w') as f:
            await f.write(json.dumps(data, indent=2, default=str))
        
        # Update metadata cache if metadata changed
        if "metadata" in data:
            metadata = TripMetadata(**data["metadata"])
            await self.save_metadata(metadata)
    
    async def get_trip(self, trip_id: str) -> Optional[Dict]:
        """Get full trip data"""
        data_file = self.data_path / f"{trip_id}.json"
        
        if not data_file.exists():
            return None
        
        async with aiofiles.open(data_file, 'r') as f:
            content = await f.read()
            return json.loads(content)
    
    async def get_trip_metadata(self, trip_id: str) -> Optional[TripMetadata]:
        """Get trip metadata only (fast)"""
        return self._metadata_cache.get(trip_id)
    
    async def list_trips(self, 
                         profile_id: Optional[str] = None,
                         status: Optional[str] = None,
                         limit: int = 50,
                         offset: int = 0) -> List[TripMetadata]:
        """List trips with filtering"""
        trips = list(self._metadata_cache.values())
        
        # Filter by profile
        if profile_id:
            trips = [t for t in trips if t.profile_id == profile_id]
        
        # Filter by status
        if status:
            trips = [t for t in trips if t.status == status]
        
        # Sort by updated_at (newest first)
        trips.sort(key=lambda t: t.updated_at, reverse=True)
        
        # Apply pagination
        return trips[offset:offset + limit]
    
    async def search_trips(self, query: str) -> List[TripMetadata]:
        """Search trips by destination or tags"""
        query_lower = query.lower()
        results = []
        
        for trip in self._metadata_cache.values():
            # Search in destination
            if query_lower in trip.destination.lower():
                results.append(trip)
                continue
            
            # Search in tags
            if any(query_lower in tag.lower() for tag in trip.tags):
                results.append(trip)
                continue
            
            # Search in travelers
            if any(query_lower in traveler.lower() 
                   for traveler in trip.travelers):
                results.append(trip)
        
        return results
    
    async def update_trip_status(self, trip_id: str, status: str):
        """Update trip processing status"""
        metadata = self._metadata_cache.get(trip_id)
        if metadata:
            metadata.status = status
            metadata.updated_at = datetime.now().isoformat()
            await self.save_metadata(metadata)
    
    async def add_to_trip(self, trip_id: str, section: str, data: Any):
        """Add data to a specific section of the trip"""
        trip = await self.get_trip(trip_id)
        if not trip:
            return False
        
        # Update the specific section
        trip[section] = data
        
        # If updating extracted data, update metadata
        if section == "extracted_data" and isinstance(data, dict):
            metadata = self._metadata_cache.get(trip_id)
            if metadata:
                if "destination" in data:
                    metadata.destination = data["destination"]
                if "start_date" in data:
                    metadata.start_date = data["start_date"]
                if "end_date" in data:
                    metadata.end_date = data["end_date"]
                if "travelers" in data:
                    metadata.travelers = data.get("travelers", [])
                await self.save_metadata(metadata)
        
        await self.save_trip_data(trip_id, trip)
        return True
    
    async def delete_trip(self, trip_id: str) -> bool:
        """Delete a trip and all associated data"""
        try:
            # Delete metadata
            metadata_file = self.metadata_path / f"{trip_id}.json"
            if metadata_file.exists():
                metadata_file.unlink()
            
            # Delete data
            data_file = self.data_path / f"{trip_id}.json"
            if data_file.exists():
                data_file.unlink()
            
            # Delete uploads
            upload_dir = self.uploads_path / trip_id
            if upload_dir.exists():
                import shutil
                shutil.rmtree(upload_dir)
            
            # Remove from cache
            if trip_id in self._metadata_cache:
                del self._metadata_cache[trip_id]
            
            return True
        except Exception as e:
            print(f"Error deleting trip {trip_id}: {e}")
            return False
    
    async def cleanup_old_trips(self, days: int = 30):
        """Clean up trips older than specified days"""
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        for trip_id, metadata in list(self._metadata_cache.items()):
            try:
                updated_at = datetime.fromisoformat(metadata.updated_at)
                if updated_at < cutoff_date and metadata.status != "completed":
                    if await self.delete_trip(trip_id):
                        deleted_count += 1
            except Exception as e:
                print(f"Error checking trip {trip_id}: {e}")
        
        return deleted_count
    
    async def get_trip_statistics(self) -> Dict:
        """Get statistics about stored trips"""
        total_trips = len(self._metadata_cache)
        
        status_counts = {}
        destination_counts = {}
        
        for metadata in self._metadata_cache.values():
            # Count by status
            status_counts[metadata.status] = (
                status_counts.get(metadata.status, 0) + 1)
            
            # Count by destination
            dest = metadata.destination
            if dest and dest != "Unknown":
                destination_counts[dest] = destination_counts.get(dest, 0) + 1
        
        # Calculate storage size
        total_size = 0
        for file in self.data_path.glob("*.json"):
            total_size += file.stat().st_size
        
        return {
            "total_trips": total_trips,
            "status_breakdown": status_counts,
            "popular_destinations": sorted(
                destination_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10],
            "storage_size_mb": round(total_size / (1024 * 1024), 2)
        }
    
    async def export_trip(self, trip_id: str) -> Optional[Dict]:
        """Export trip data for backup or sharing"""
        trip = await self.get_trip(trip_id)
        if not trip:
            return None
        
        # Include metadata
        metadata = self._metadata_cache.get(trip_id)
        if metadata:
            trip["metadata"] = asdict(metadata)
        
        return trip
    
    async def import_trip(self, trip_data: Dict) -> str:
        """Import a trip from exported data"""
        # Generate new trip ID to avoid conflicts
        new_trip_id = str(uuid.uuid4())
        
        # Update trip ID in data
        trip_data["trip_id"] = new_trip_id
        if "metadata" in trip_data:
            trip_data["metadata"]["trip_id"] = new_trip_id
            trip_data["metadata"]["created_at"] = datetime.now().isoformat()
            trip_data["metadata"]["updated_at"] = datetime.now().isoformat()
        
        # Save the trip
        await self.save_trip_data(new_trip_id, trip_data)
        
        return new_trip_id
