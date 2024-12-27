import os
from datetime import timedelta

class TestConfig:
    """Test configuration."""
    
    TESTING = True
    DEBUG = True
    
    # Use a separate database for testing
    MONGO_URI = "mongodb://localhost:27017/skriptd_test"
    
    # JWT settings
    JWT_SECRET_KEY = "test-secret-key"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # CORS settings
    CORS_ORIGINS = "*"
    
    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = "test_uploads"
    
    # Rate limiting
    RATELIMIT_DEFAULT = "100 per minute"
    RATELIMIT_STORAGE_URL = "memory://"
