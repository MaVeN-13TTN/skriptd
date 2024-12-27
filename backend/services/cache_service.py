from functools import wraps
import json
from typing import Any, Optional, Union
from redis import Redis
from datetime import timedelta
import os

class CacheService:
    def __init__(self):
        self.redis = Redis.from_url(
            os.getenv('CACHE_REDIS_URL', 'redis://localhost:6379/0'),
            decode_responses=True
        )
        self.default_timeout = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))
        self.key_prefix = os.getenv('CACHE_KEY_PREFIX', 'skriptd_')

    def _make_key(self, key: str) -> str:
        """Create a prefixed key for Redis."""
        return f"{self.key_prefix}{key}"

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        value = self.redis.get(self._make_key(key))
        if value:
            return json.loads(value)
        return None

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """Set a value in cache with optional timeout."""
        timeout = timeout or self.default_timeout
        try:
            return self.redis.setex(
                self._make_key(key),
                timedelta(seconds=timeout),
                json.dumps(value)
            )
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        return bool(self.redis.delete(self._make_key(key)))

    def clear(self, pattern: str = "*") -> bool:
        """Clear all keys matching pattern."""
        try:
            keys = self.redis.keys(self._make_key(pattern))
            if keys:
                return bool(self.redis.delete(*keys))
            return True
        except Exception:
            return False

def cached(timeout: Optional[int] = None, key_pattern: Optional[str] = None):
    """Decorator for caching function results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = CacheService()
            
            # Generate cache key
            if key_pattern:
                cache_key = key_pattern.format(*args, **kwargs)
            else:
                # Default key pattern: function_name:arg1:arg2:...
                cache_key = f"{func.__name__}:" + ":".join(
                    [str(arg) for arg in args] +
                    [f"{k}={v}" for k, v in sorted(kwargs.items())]
                )
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # If not in cache, execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
            
        return wrapper
    return decorator

# Example usage:
"""
@cached(timeout=300, key_pattern="note:{0}")
def get_note(note_id: str) -> dict:
    # Function implementation
    pass

@cached(timeout=3600)
def get_user_notes(user_id: str) -> list:
    # Function implementation
    pass
"""
