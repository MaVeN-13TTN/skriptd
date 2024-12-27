from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import timedelta
from dotenv import load_dotenv
import os
import time
from datetime import datetime

# Local imports
from logging_config import setup_logging
from errors import register_error_handlers
from middleware.request_logger import log_request
from middleware.rate_limiter import rate_limit
from extensions import mongo, jwt, socketio, mail

def create_app(config_object=None):
    # Load environment variables
    load_dotenv()

    # Initialize Flask app
    app = Flask(__name__)

    # Load configuration
    if config_object:
        app.config.from_object(config_object)
    else:
        app.config.from_object('config.Config')

    # Setup logging
    app = setup_logging(app)

    # Configure MongoDB
    app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/skriptd")
    mongo.init_app(app)

    # Configure JWT
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "your-secret-key")  # Change in production
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    jwt.init_app(app)

    # Initialize SocketIO
    socketio.init_app(app, cors_allowed_origins="*")

    # Initialize Mail
    mail.init_app(app)

    # Enable CORS
    CORS(app)

    # Register error handlers
    register_error_handlers(app)

    # Import routes after app initialization to avoid circular imports
    from routes.auth import auth_bp
    from routes.notes import notes_bp
    from routes.tags import tags_bp
    from routes.versions import versions_bp
    from routes.attachments import attachments_bp
    from routes.folders import folders_bp
    from routes.search import search_bp
    from routes.sync import sync_bp

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(notes_bp, url_prefix='/api/notes')
    app.register_blueprint(tags_bp, url_prefix='/api/tags')
    app.register_blueprint(versions_bp, url_prefix='/api/versions')
    app.register_blueprint(attachments_bp, url_prefix='/api/attachments')
    app.register_blueprint(folders_bp, url_prefix='/api/folders')
    app.register_blueprint(search_bp, url_prefix='/api/search')
    app.register_blueprint(sync_bp, url_prefix='/api/sync')

    @app.before_request
    def before_request():
        """Global middleware for all requests."""
        # Skip middleware for health check
        if request.endpoint == 'health_check':
            return
        
        # Apply rate limiting
        rate_limit()
        
        # Log request
        log_request()

    @app.after_request
    def after_request(response):
        """Global middleware for all responses."""
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Log response
        app.logger.info(f'Response: {response.status}')
        
        return response

    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        })

    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.socketio.run(app, debug=app.config['DEBUG'], host='0.0.0.0', port=5000)
