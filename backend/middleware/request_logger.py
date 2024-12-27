import time
import logging
from flask import request, g
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def log_request():
    """Log incoming request details."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Start timer
            start_time = time.time()
            
            # Log request details
            logger.info(f"Request: {request.method} {request.url}")
            logger.info(f"Headers: {dict(request.headers)}")
            
            if request.is_json:
                logger.info(f"Body: {request.get_json()}")
                
            # Store start time in g object
            g.start_time = start_time
            
            # Execute route handler
            response = f(*args, **kwargs)
            
            # Calculate request duration
            duration = time.time() - g.start_time
            
            # Log response details
            logger.info(f"Response Time: {duration:.2f}s")
            logger.info(f"Response Status: {response.status_code}")
            
            return response
        return decorated_function
    return decorator
