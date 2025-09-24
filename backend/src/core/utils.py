"""
Core utility functions
"""
import uuid
import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from pathlib import Path


def generate_uuid() -> str:
    """Generate a UUID4 string"""
    return str(uuid.uuid4())


def generate_short_id(length: int = 8) -> str:
    """Generate a short random ID"""
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def hash_string(text: str) -> str:
    """Generate SHA256 hash of a string"""
    return hashlib.sha256(text.encode()).hexdigest()


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    # Convert to lowercase and replace spaces with hyphens
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely parse JSON string"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, default: Any = None) -> str:
    """Safely serialize object to JSON"""
    try:
        return json.dumps(obj, default=str)
    except (TypeError, ValueError):
        return json.dumps(default) if default is not None else "{}"


def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return Path(filename).suffix.lower().lstrip('.')


def get_file_size(file_path: Union[str, Path]) -> int:
    """Get file size in bytes"""
    return Path(file_path).stat().st_size


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def utc_now() -> datetime:
    """Get current UTC datetime"""
    return datetime.now(timezone.utc)


def format_datetime(
    dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """Format datetime to string"""
    return dt.strftime(format_str)


def parse_datetime(
    dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S"
) -> Optional[datetime]:
    """Parse datetime string"""
    try:
        return datetime.strptime(dt_str, format_str)
    except ValueError:
        return None


def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if (key in result and isinstance(result[key], dict) and 
            isinstance(value, dict)):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """Flatten nested dictionary"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def remove_duplicates(lst: List, key: Optional[str] = None) -> List:
    """Remove duplicates from list"""
    if key is None:
        return list(dict.fromkeys(lst))
    
    seen = set()
    result = []
    for item in lst:
        item_key = (item.get(key) if isinstance(item, dict) 
                    else getattr(item, key, None))
        if item_key not in seen:
            seen.add(item_key)
            result.append(item)
    
    return result


def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """Sanitize string for safe storage/display"""
    if not text:
        return ""
    
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length].rstrip()
    
    return text


def is_valid_email(email: str) -> bool:
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_url(url: str) -> bool:
    """Basic URL validation"""
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def extract_numbers(text: str) -> List[float]:
    """Extract all numbers from text"""
    pattern = r'-?\d+\.?\d*'
    matches = re.findall(pattern, text)
    return [float(match) for match in matches if match]


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
