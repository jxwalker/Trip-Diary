"""
Simple file-based database for trip persistence
Uses JSON files to store trip data
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import aiofiles

class TripDatabase:
    def __init__(self):
        # Create data directory if it doesn't exist
        self.data_dir = Path(__file__).parent / "data" / "trips"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Index file to track all trips
        self.index_file = self.data_dir / "index.json"
        if not self.index_file.exists():
            self._save_index({})
    
    def _save_index(self, index: Dict):
        """Save index to file"""
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def _load_index(self) -> Dict:
        """Load index from file"""
        try:
            with open(self.index_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    async def save_trip(
        self, trip_id: str, trip_data: Dict, user_id: str = "default"
    ) -> bool:
        """Save a trip to the database"""
        try:
            # Add metadata
            trip_data["saved_at"] = datetime.now().isoformat()
            trip_data["user_id"] = user_id
            trip_data["trip_id"] = trip_id
            
            # Extract summary info for index
            itinerary = trip_data.get("itinerary", {})
            trip_summary = itinerary.get("trip_summary", {})
            
            # Save full trip data
            trip_file = self.data_dir / f"{trip_id}.json"
            async with aiofiles.open(trip_file, 'w') as f:
                await f.write(json.dumps(trip_data, indent=2))
            
            # Update index
            index = self._load_index()
            index[trip_id] = {
                "trip_id": trip_id,
                "user_id": user_id,
                "destination": trip_summary.get("destination", "Unknown"),
                "start_date": trip_summary.get("start_date", ""),
                "end_date": trip_summary.get("end_date", ""),
                "duration": trip_summary.get("duration", ""),
                "saved_at": trip_data["saved_at"],
                "title": (
                    f"{trip_summary.get('destination', 'Trip')} - "
                    f"{trip_summary.get('start_date', '')}"
                ),
                "passengers": len(itinerary.get("passengers", [])),
                "flights": len(itinerary.get("flights", [])),
                "hotels": len(itinerary.get("accommodations", []))
            }
            self._save_index(index)
            
            return True
        except Exception as e:
            print(f"Error saving trip: {e}")
            return False
    
    async def load_trip(self, trip_id: str) -> Optional[Dict]:
        """Load a trip from the database"""
        try:
            trip_file = self.data_dir / f"{trip_id}.json"
            if not trip_file.exists():
                return None
            
            async with aiofiles.open(trip_file, 'r') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            print(f"Error loading trip: {e}")
            return None
    
    async def update_trip_enhanced_guide(
        self, trip_id: str, enhanced_guide: Dict
    ) -> bool:
        """Update a trip with enhanced guide data"""
        try:
            # Load existing trip
            trip_data = await self.load_trip(trip_id)
            if not trip_data:
                print(f"Trip {trip_id} not found for update")
                return False
            
            # Add enhanced guide
            trip_data["enhanced_guide"] = enhanced_guide
            trip_data["enhanced_guide_generated_at"] = (
                datetime.now().isoformat()
            )
            
            # Save updated trip
            trip_file = self.data_dir / f"{trip_id}.json"
            async with aiofiles.open(trip_file, 'w') as f:
                await f.write(json.dumps(trip_data, indent=2))
            
            # Update index to reflect guide generation
            index = self._load_index()
            if trip_id in index:
                index[trip_id]["has_enhanced_guide"] = True
                index[trip_id]["guide_generated_at"] = (
                    trip_data["enhanced_guide_generated_at"]
                )
                self._save_index(index)
            
            print(
                f"[DEBUG] Successfully saved enhanced guide for trip {trip_id}"
            )
            return True
        except Exception as e:
            print(f"Error updating trip with enhanced guide: {e}")
            return False
    
    async def list_trips(self, user_id: str = "default") -> List[Dict]:
        """List all trips for a user"""
        try:
            index = self._load_index()
            # Filter by user_id and sort by saved_at
            user_trips = [
                trip for trip in index.values() 
                if trip.get("user_id") == user_id
            ]
            # Sort by saved_at date (newest first)
            user_trips.sort(key=lambda x: x.get("saved_at", ""), reverse=True)
            return user_trips
        except Exception as e:
            print(f"Error listing trips: {e}")
            return []
    
    async def delete_trip(self, trip_id: str) -> bool:
        """Delete a trip from the database"""
        try:
            # Remove file
            trip_file = self.data_dir / f"{trip_id}.json"
            if trip_file.exists():
                trip_file.unlink()
            
            # Update index
            index = self._load_index()
            if trip_id in index:
                del index[trip_id]
                self._save_index(index)
            
            return True
        except Exception as e:
            print(f"Error deleting trip: {e}")
            return False
    
    async def search_trips(
        self, query: str, user_id: str = "default"
    ) -> List[Dict]:
        """Search trips by destination or date"""
        try:
            trips = await self.list_trips(user_id)
            query_lower = query.lower()
            
            return [
                trip for trip in trips
                if query_lower in trip.get("destination", "").lower()
                or query_lower in trip.get("start_date", "")
                or query_lower in trip.get("end_date", "")
                or query_lower in trip.get("title", "").lower()
            ]
        except Exception as e:
            print(f"Error searching trips: {e}")
            return []
