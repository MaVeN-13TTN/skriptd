from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps
from flask import request, jsonify
from extensions import mongo
from bson import ObjectId

def auth_required(f):
    """Authentication middleware that verifies JWT and loads user."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        
        # Get user ID from JWT
        current_user_id = get_jwt_identity()
        
        # Load user from database
        user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        if not user:
            return {'error': 'User not found'}, 401
            
        # Store user in g object for route handlers
        g.user = user
        
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    """Role-based authorization middleware."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            
            current_user_id = get_jwt_identity()
            user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
            
            if not user:
                return {'error': 'User not found'}, 401
                
            user_roles = user.get('roles', [])
            if not any(role in user_roles for role in roles):
                return {'error': 'Insufficient permissions'}, 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
