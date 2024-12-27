from flask import request, g
from functools import wraps
import time
from collections import defaultdict
import threading

class RateLimiter:
    def __init__(self, requests=100, window=60):
        self.requests = requests  # Number of requests allowed
        self.window = window  # Time window in seconds
        self.clients = defaultdict(list)
        self.lock = threading.Lock()

    def is_allowed(self, client_id):
        """Check if client is allowed to make a request."""
        with self.lock:
            now = time.time()
            
            # Remove old requests
            self.clients[client_id] = [
                timestamp for timestamp in self.clients[client_id]
                if now - timestamp < self.window
            ]
            
            # Check if client has exceeded rate limit
            if len(self.clients[client_id]) >= self.requests:
                return False
                
            # Add new request
            self.clients[client_id].append(now)
            return True

rate_limiter = RateLimiter()

def rate_limit(f):
    """Rate limiting decorator."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_id = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        if not rate_limiter.is_allowed(client_id):
            return {
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please try again later.'
            }, 429
            
        return f(*args, **kwargs)
    return decorated_function
