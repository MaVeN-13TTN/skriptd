from prometheus_client import Counter, Histogram, Info, start_http_server
import time
import threading
import os

# Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration_seconds = Histogram(
    'request_duration_seconds',
    'HTTP request duration in seconds',
    ['endpoint']
)

api_info = Info('api_info', 'API information')

# Custom metrics
note_operations = Counter(
    'note_operations_total',
    'Total note operations',
    ['operation']
)

ai_requests = Counter(
    'ai_requests_total',
    'Total AI service requests',
    ['operation']
)

collaboration_sessions = Counter(
    'collaboration_sessions_total',
    'Total collaboration sessions'
)

export_operations = Counter(
    'export_operations_total',
    'Total export operations',
    ['format']
)

class MetricsMiddleware:
    def __init__(self, app):
        self.app = app
        
        # Start Prometheus metrics server
        if os.getenv('ENABLE_METRICS', 'True').lower() == 'true':
            metrics_port = int(os.getenv('METRICS_PORT', '9090'))
            threading.Thread(target=lambda: start_http_server(metrics_port)).start()
        
        # Set API info
        api_info.info({
            'version': '1.0.0',
            'environment': os.getenv('ENVIRONMENT', 'development')
        })

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        method = environ.get('REQUEST_METHOD', '')
        
        # Start timer
        start_time = time.time()
        
        def custom_start_response(status, headers, exc_info=None):
            # Record metrics
            status_code = status.split()[0]
            http_requests_total.labels(
                method=method,
                endpoint=path,
                status=status_code
            ).inc()
            
            # Record request duration
            duration = time.time() - start_time
            request_duration_seconds.labels(
                endpoint=path
            ).observe(duration)
            
            return start_response(status, headers, exc_info)
        
        return self.app(environ, custom_start_response)

# Decorator for tracking operation metrics
def track_operation(metric, label=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if label:
                metric.labels(label).inc()
            else:
                metric.inc()
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Example usage:
"""
@track_operation(note_operations, 'create')
def create_note():
    pass

@track_operation(ai_requests, 'summarize')
def summarize_note():
    pass
"""
