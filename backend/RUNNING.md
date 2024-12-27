# Detailed Guide: Running Skript'd Backend Components

This guide provides detailed instructions for running each component of the Skript'd backend system.

## 1. Core Services Setup

### MongoDB Setup
```bash
# Start MongoDB
sudo systemctl start mongodb

# Verify MongoDB is running
sudo systemctl status mongodb

# Create database and user
mongosh
> use skriptd
> db.createUser({
    user: "skriptd_user",
    pwd: "your_password",
    roles: ["readWrite"]
})
```

### Redis Setup
```bash
# Start Redis
sudo systemctl start redis-server

# Verify Redis is running
redis-cli ping  # Should return PONG

# Monitor Redis in real-time (useful for debugging)
redis-cli monitor
```

### Elasticsearch Setup
```bash
# Start Elasticsearch
sudo systemctl start elasticsearch

# Wait for it to start (usually takes 10-20 seconds)
sleep 20

# Verify Elasticsearch is running
curl -X GET "localhost:9200/"

# Check cluster health
curl -X GET "localhost:9200/_cluster/health"
```

## 2. Environment Configuration

Create and configure your `.env` file:

```bash
# Copy example configuration
cp .env.example .env

# Edit the .env file with your settings
nano .env
```

Essential configurations:
```env
# Core Settings
FLASK_APP=app.py
FLASK_ENV=development
PORT=5000

# Database
MONGODB_URI=mongodb://skriptd_user:your_password@localhost:27017/skriptd

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
CACHE_REDIS_URL=redis://localhost:6379/1
CELERY_BROKER_URL=redis://localhost:6379/2
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Elasticsearch
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_INDEX=skriptd

# API Keys
OPENAI_API_KEY=your_openai_api_key

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret
JWT_ACCESS_TOKEN_EXPIRES=3600
```

## 3. Running the Application

### Main Flask Application
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies (if not done already)
pip install -r requirements.txt

# Run Flask development server
flask run --host=0.0.0.0 --port=5000

# Or for production (using gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### Background Task Workers

#### Celery Worker
```bash
# Start main Celery worker
celery -A tasks worker --loglevel=info --concurrency=4

# Start worker with specific queues
celery -A tasks worker -Q high_priority,default --loglevel=info

# Start worker with autoscaling
celery -A tasks worker --autoscale=10,3 --loglevel=info
```

#### Celery Beat (Scheduler)
```bash
# Start Celery beat for scheduled tasks
celery -A tasks beat --loglevel=info
```

#### Flower (Monitoring)
```bash
# Start Flower on default port (5555)
celery -A tasks flower

# Start with custom port and settings
celery -A tasks flower --port=5555 --basic_auth=user:pass
```

## 4. Monitoring Setup

### Prometheus
```bash
# Start Prometheus (assuming config is in /etc/prometheus/prometheus.yml)
prometheus --config.file=/etc/prometheus/prometheus.yml

# Verify metrics endpoint
curl http://localhost:9090/metrics
```

### Grafana
```bash
# Start Grafana
sudo systemctl start grafana-server

# Access Grafana UI
# Open http://localhost:3000 in your browser
# Default credentials: admin/admin
```

## 5. Development Tools

### Running Tests
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_ai_service.py

# Run tests with verbose output
pytest -v

# Run tests that match a pattern
pytest -k "test_ai"
```

### Code Formatting
```bash
# Format code with black
black .

# Check code style with flake8
flake8

# Sort imports
isort .
```

## 6. Logging and Debugging

### View Logs
```bash
# View Flask application logs
tail -f logs/app.log

# View Celery worker logs
tail -f logs/celery.log

# View combined logs
tail -f logs/*.log
```

### Debug Mode
```bash
# Run Flask in debug mode
FLASK_DEBUG=1 flask run

# Debug Celery tasks
celery -A tasks worker --loglevel=debug
```

## 7. Health Checks

```bash
# Check Flask application
curl http://localhost:5000/health

# Check Redis
redis-cli ping

# Check MongoDB
mongosh --eval "db.runCommand({ ping: 1 })"

# Check Elasticsearch
curl -X GET "localhost:9200/_cluster/health"

# Check Celery
celery -A tasks inspect ping
```

## 8. Common Operations

### Reset Cache
```bash
# Clear all Redis caches
redis-cli
> FLUSHALL

# Clear specific database
redis-cli -n 1 FLUSHDB
```

### Manage Tasks
```bash
# List active tasks
celery -A tasks inspect active

# Revoke a task
celery -A tasks revoke <task_id>

# Purge all tasks
celery -A tasks purge
```

### Database Operations
```bash
# Create database backup
mongodump --db skriptd --out /backup/$(date +%Y%m%d)

# Restore database
mongorestore --db skriptd /backup/20240101/skriptd/
```

## 9. Production Deployment

For production deployment, additional steps are recommended:

1. **Use NGINX as reverse proxy**
```nginx
server {
    listen 80;
    server_name api.skriptd.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

2. **Use Supervisor for process management**
```ini
[program:skriptd_api]
command=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
directory=/path/to/backend
user=skriptd
autostart=true
autorestart=true

[program:skriptd_celery]
command=/path/to/venv/bin/celery -A tasks worker --loglevel=info
directory=/path/to/backend
user=skriptd
autostart=true
autorestart=true
```

3. **Enable SSL/TLS**
```bash
# Using certbot with NGINX
sudo certbot --nginx -d api.skriptd.com
```

## 10. Troubleshooting

### Common Issues and Solutions

1. **Redis Connection Errors**
```bash
# Check Redis service
sudo systemctl status redis-server

# Check Redis configuration
redis-cli CONFIG GET *

# Test connection
redis-cli -h localhost -p 6379 ping
```

2. **Celery Task Issues**
```bash
# Check active workers
celery -A tasks inspect active

# Check reserved tasks
celery -A tasks inspect reserved

# Check task queue
celery -A tasks inspect scheduled
```

3. **MongoDB Issues**
```bash
# Check MongoDB logs
sudo tail -f /var/log/mongodb/mongodb.log

# Check MongoDB status
sudo systemctl status mongodb

# Repair database
mongosh
> use skriptd
> db.repairDatabase()
```

4. **Elasticsearch Issues**
```bash
# Check cluster health
curl -X GET "localhost:9200/_cluster/health?pretty"

# Check indices
curl -X GET "localhost:9200/_cat/indices?v"

# Clear cache
curl -X POST "localhost:9200/_cache/clear"
```

Remember to always check the logs when troubleshooting:
- Application logs: `logs/app.log`
- Celery logs: `logs/celery.log`
- NGINX logs: `/var/log/nginx/error.log`
- System logs: `journalctl -u skriptd_*`
