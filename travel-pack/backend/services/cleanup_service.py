"""
Cleanup Service for TTL management of uploaded files and outputs
Prevents disk bloat by automatically removing old files
"""

import os
import time
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class CleanupService:
    """
    Service to manage automatic cleanup of temporary files
    """
    
    def __init__(self, uploads_dir: str = "uploads", outputs_dir: str = "output", ttl_hours: int = 24):
        """
        Initialize cleanup service
        
        Args:
            uploads_dir: Directory containing uploaded files
            outputs_dir: Directory containing generated output files
            ttl_hours: Time to live in hours before files are deleted
        """
        self.uploads_dir = Path(uploads_dir)
        self.outputs_dir = Path(outputs_dir)
        self.ttl_seconds = ttl_hours * 3600
        
    def _should_delete_file(self, file_path: Path) -> bool:
        """Check if a file should be deleted based on age"""
        try:
            file_age = time.time() - file_path.stat().st_mtime
            return file_age > self.ttl_seconds
        except Exception as e:
            logger.error(f"Error checking file age for {file_path}: {e}")
            return False
    
    def cleanup_directory(self, directory: Path) -> int:
        """
        Clean up old files in a directory
        
        Returns:
            Number of files deleted
        """
        deleted_count = 0
        
        if not directory.exists():
            return 0
            
        try:
            # Iterate through all files in directory and subdirectories
            for file_path in directory.rglob("*"):
                if file_path.is_file() and self._should_delete_file(file_path):
                    try:
                        file_path.unlink()
                        deleted_count += 1
                        logger.info(f"Deleted old file: {file_path}")
                    except Exception as e:
                        logger.error(f"Failed to delete {file_path}: {e}")
                        
            # Remove empty directories
            for dir_path in sorted(directory.rglob("*/"), reverse=True):
                try:
                    if dir_path.is_dir() and not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        logger.info(f"Removed empty directory: {dir_path}")
                except Exception as e:
                    logger.error(f"Failed to remove directory {dir_path}: {e}")
                    
        except Exception as e:
            logger.error(f"Error during cleanup of {directory}: {e}")
            
        return deleted_count
    
    async def cleanup_all(self) -> dict:
        """
        Clean up all managed directories
        
        Returns:
            Dictionary with cleanup statistics
        """
        stats = {
            "uploads_deleted": 0,
            "outputs_deleted": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Clean uploads directory
        stats["uploads_deleted"] = self.cleanup_directory(self.uploads_dir)
        
        # Clean outputs directory  
        stats["outputs_deleted"] = self.cleanup_directory(self.outputs_dir)
        
        logger.info(f"Cleanup completed: {stats}")
        return stats
    
    async def start_periodic_cleanup(self, interval_hours: int = 1):
        """
        Start periodic cleanup task that runs every interval_hours
        
        Args:
            interval_hours: How often to run cleanup (default: every hour)
        """
        while True:
            try:
                await self.cleanup_all()
            except Exception as e:
                logger.error(f"Error in periodic cleanup: {e}")
            
            # Wait for next cleanup cycle
            await asyncio.sleep(interval_hours * 3600)


class FileManager:
    """
    Manager for creating files with automatic TTL tracking
    """
    
    def __init__(self, base_dir: str, cleanup_service: Optional[CleanupService] = None):
        """
        Initialize file manager
        
        Args:
            base_dir: Base directory for file operations
            cleanup_service: Optional cleanup service instance
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.cleanup_service = cleanup_service
        
    def create_temp_file(self, content: bytes, suffix: str = ".pdf", prefix: str = "temp_") -> Path:
        """
        Create a temporary file with automatic cleanup tracking
        
        Args:
            content: File content as bytes
            suffix: File suffix/extension
            prefix: File prefix
            
        Returns:
            Path to created file
        """
        # Create unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}{timestamp}_{os.urandom(4).hex()}{suffix}"
        file_path = self.base_dir / filename
        
        # Write content
        file_path.write_bytes(content)
        
        # Log creation for tracking
        logger.info(f"Created temporary file: {file_path}")
        
        return file_path
    
    def get_file_age_hours(self, file_path: Path) -> float:
        """Get age of file in hours"""
        if not file_path.exists():
            return -1
        
        file_age_seconds = time.time() - file_path.stat().st_mtime
        return file_age_seconds / 3600