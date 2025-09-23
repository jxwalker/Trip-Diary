"""
Database Configuration
"""
from pydantic import Field, validator
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional


class DatabaseConfig(BaseSettings):
    """Database configuration"""
    
    # Database type and connection
    type: str = Field(default="file", env="DB_TYPE")  # file, sqlite, postgresql
    path: str = Field(default="data", env="DB_PATH")
    
    # SQLite specific (if using SQLite)
    sqlite_file: str = Field(default="tripcraft.db", env="DB_SQLITE_FILE")
    
    # PostgreSQL specific (if using PostgreSQL)
    postgres_host: Optional[str] = Field(default=None, env="DB_POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="DB_POSTGRES_PORT")
    postgres_user: Optional[str] = Field(default=None, env="DB_POSTGRES_USER")
    postgres_password: Optional[str] = Field(
        default=None, env="DB_POSTGRES_PASSWORD"
    )
    postgres_database: Optional[str] = Field(
        default=None, env="DB_POSTGRES_DATABASE"
    )
    
    # Connection settings
    pool_size: int = Field(default=5, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=10, env="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")
    
    # Backup settings
    backup_enabled: bool = Field(default=True, env="DB_BACKUP_ENABLED")
    backup_interval_hours: int = Field(
        default=24, env="DB_BACKUP_INTERVAL_HOURS"
    )
    backup_retention_days: int = Field(
        default=7, env="DB_BACKUP_RETENTION_DAYS"
    )
    backup_path: str = Field(default="backups", env="DB_BACKUP_PATH")
    
    # Performance settings
    cache_enabled: bool = Field(default=True, env="DB_CACHE_ENABLED")
    cache_size: int = Field(default=1000, env="DB_CACHE_SIZE")
    cache_ttl_seconds: int = Field(default=300, env="DB_CACHE_TTL_SECONDS")
    
    @validator('type')
    def validate_db_type(cls, v):
        """Validate database type"""
        valid_types = ['file', 'sqlite', 'postgresql']
        if v not in valid_types:
            raise ValueError(f'Database type must be one of: {valid_types}')
        return v
    
    def get_database_path(self) -> Path:
        """Get database directory path"""
        return Path(self.path).resolve()
    
    def get_backup_path(self) -> Path:
        """Get backup directory path"""
        return Path(self.backup_path).resolve()
    
    def get_sqlite_file_path(self) -> Path:
        """Get SQLite file path"""
        return self.get_database_path() / self.sqlite_file
    
    def get_connection_string(self) -> str:
        """Get database connection string"""
        if self.type == "file":
            return f"file://{self.get_database_path()}"
        elif self.type == "sqlite":
            return f"sqlite:///{self.get_sqlite_file_path()}"
        elif self.type == "postgresql":
            if not all([
                self.postgres_host, self.postgres_user, 
                self.postgres_password, self.postgres_database
            ]):
                raise ValueError(
                    "PostgreSQL connection requires host, user, password, and database"
                )
            return (
                f"postgresql://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"
            )
        else:
            raise ValueError(f"Unsupported database type: {self.type}")
    
    class Config:
        env_prefix = "DB_"
