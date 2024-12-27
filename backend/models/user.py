from datetime import datetime
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    """User model."""
    
    def __init__(self, username, email, password=None, _id=None):
        self._id = _id or ObjectId()
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password) if password else None
        self.is_verified = False
        self.verification_token = None
        self.reset_token = None
        self.reset_token_expires = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    @staticmethod
    def create(mongo, username, email, password):
        """Create a new user."""
        user = User(username, email, password)
        mongo.db.users.insert_one(user.to_dict())
        return user
    
    @staticmethod
    def get_by_id(mongo, user_id):
        """Get user by ID."""
        data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        return User.from_dict(data) if data else None
    
    @staticmethod
    def get_by_email(mongo, email):
        """Get user by email."""
        data = mongo.db.users.find_one({'email': email})
        return User.from_dict(data) if data else None
    
    def verify_password(self, password):
        """Verify password."""
        return check_password_hash(self.password_hash, password)
    
    def set_password(self, mongo, password):
        """Set new password."""
        self.password_hash = generate_password_hash(password)
        self.updated_at = datetime.utcnow()
        mongo.db.users.update_one(
            {'_id': self._id},
            {'$set': {'password_hash': self.password_hash, 'updated_at': self.updated_at}}
        )
    
    def set_verification_token(self, mongo, token):
        """Set verification token."""
        self.verification_token = token
        self.updated_at = datetime.utcnow()
        mongo.db.users.update_one(
            {'_id': self._id},
            {'$set': {
                'verification_token': token,
                'updated_at': self.updated_at
            }}
        )
    
    def verify_email(self, mongo):
        """Verify user's email."""
        self.is_verified = True
        self.verification_token = None
        self.updated_at = datetime.utcnow()
        mongo.db.users.update_one(
            {'_id': self._id},
            {'$set': {
                'is_verified': True,
                'verification_token': None,
                'updated_at': self.updated_at
            }}
        )
    
    def set_reset_token(self, mongo, token, expires):
        """Set password reset token."""
        self.reset_token = token
        self.reset_token_expires = expires
        self.updated_at = datetime.utcnow()
        mongo.db.users.update_one(
            {'_id': self._id},
            {'$set': {
                'reset_token': token,
                'reset_token_expires': expires,
                'updated_at': self.updated_at
            }}
        )
    
    def clear_reset_token(self, mongo):
        """Clear password reset token."""
        self.reset_token = None
        self.reset_token_expires = None
        self.updated_at = datetime.utcnow()
        mongo.db.users.update_one(
            {'_id': self._id},
            {'$set': {
                'reset_token': None,
                'reset_token_expires': None,
                'updated_at': self.updated_at
            }}
        )
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            '_id': self._id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'is_verified': self.is_verified,
            'verification_token': self.verification_token,
            'reset_token': self.reset_token,
            'reset_token_expires': self.reset_token_expires,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def from_dict(data):
        """Create from dictionary."""
        if not data:
            return None
            
        user = User(
            username=data['username'],
            email=data['email'],
            _id=data['_id']
        )
        user.password_hash = data['password_hash']
        user.is_verified = data.get('is_verified', False)
        user.verification_token = data.get('verification_token')
        user.reset_token = data.get('reset_token')
        user.reset_token_expires = data.get('reset_token_expires')
        user.created_at = data['created_at']
        user.updated_at = data['updated_at']
        return user
