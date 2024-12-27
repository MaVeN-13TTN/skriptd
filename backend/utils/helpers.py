import re
from datetime import datetime
from bson import ObjectId
import json

class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for MongoDB ObjectId and datetime objects."""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """
    Validate password strength.
    Requirements:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one number
    - Contains at least one special character
    """
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True

def sanitize_filename(filename):
    """Sanitize filename to prevent directory traversal attacks."""
    return re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

def get_file_extension(filename):
    """Get file extension from filename."""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

def format_file_size(size_bytes):
    """Format file size in bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def parse_query_params(args):
    """Parse and validate query parameters."""
    params = {}
    
    # Pagination
    try:
        params['page'] = max(1, int(args.get('page', 1)))
        params['per_page'] = min(100, max(1, int(args.get('per_page', 20))))
    except ValueError:
        params['page'] = 1
        params['per_page'] = 20
    
    # Sorting
    sort_field = args.get('sort', 'created_at')
    sort_order = args.get('order', 'desc')
    params['sort'] = (sort_field, -1 if sort_order == 'desc' else 1)
    
    return params

def generate_error_response(message, status_code=400):
    """Generate standardized error response."""
    return {
        'error': {
            'message': message,
            'status_code': status_code,
            'timestamp': datetime.utcnow().isoformat()
        }
    }, status_code
