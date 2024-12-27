import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging(app):
    """Configure application logging."""
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Configure logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # File handler for all logs
    all_logs_file = os.path.join('logs', 'skriptd.log')
    file_handler = RotatingFileHandler(
        all_logs_file,
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Error file handler for error logs
    error_logs_file = os.path.join('logs', 'error.log')
    error_file_handler = RotatingFileHandler(
        error_logs_file,
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    error_file_handler.setFormatter(formatter)
    error_file_handler.setLevel(logging.ERROR)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)

    # Remove default handlers
    app.logger.handlers = []

    # Add handlers to app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_file_handler)
    app.logger.addHandler(console_handler)

    # Set overall logging level
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)

    # Log application startup
    app.logger.info(f"Application started at {datetime.utcnow().isoformat()}")
    app.logger.info(f"Debug mode: {app.debug}")

    return app
