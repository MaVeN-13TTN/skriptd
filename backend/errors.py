from flask import jsonify
from werkzeug.exceptions import HTTPException
import logging

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base class for API errors."""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        rv['status_code'] = self.status_code
        return rv

class ValidationError(APIError):
    """Raised when input validation fails."""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=400, payload=payload)

class AuthenticationError(APIError):
    """Raised when authentication fails."""
    def __init__(self, message="Authentication required", payload=None):
        super().__init__(message, status_code=401, payload=payload)

class AuthorizationError(APIError):
    """Raised when user doesn't have required permissions."""
    def __init__(self, message="Insufficient permissions", payload=None):
        super().__init__(message, status_code=403, payload=payload)

class NotFoundError(APIError):
    """Raised when a resource is not found."""
    def __init__(self, message="Resource not found", payload=None):
        super().__init__(message, status_code=404, payload=payload)

class ConflictError(APIError):
    """Raised when there's a conflict with existing data."""
    def __init__(self, message="Resource conflict", payload=None):
        super().__init__(message, status_code=409, payload=payload)

def register_error_handlers(app):
    """Register error handlers for the Flask app."""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Handle custom API errors."""
        logger.error(f"API Error: {error.message}")
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        """Handle Werkzeug HTTP errors."""
        logger.error(f"HTTP Error: {error}")
        response = jsonify({
            'error': error.description,
            'status_code': error.code
        })
        response.status_code = error.code
        return response

    @app.errorhandler(Exception)
    def handle_generic_error(error):
        """Handle all other exceptions."""
        logger.exception("Unhandled Exception")
        response = jsonify({
            'error': 'An unexpected error occurred',
            'status_code': 500
        })
        response.status_code = 500
        return response
