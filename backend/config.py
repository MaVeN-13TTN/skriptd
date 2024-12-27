import os
from datetime import timedelta

class Config:
    """Base configuration."""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # MongoDB
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/skriptd')
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    )
    
    # Security
    SECURITY_PASSWORD_SALT = os.environ.get(
        'SECURITY_PASSWORD_SALT',
        'dev-password-salt'
    )
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # File Upload
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    
    # Rate Limiting
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '100/minute')
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
