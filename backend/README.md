# Skript'd Backend

Skript'd is an advanced note-taking application designed specifically for computer science students, featuring AI capabilities, version control, collaborative editing, and enhanced export options.

## Features

- **AI-Powered Features**
  - Note summarization
  - Code explanation
  - Code improvement suggestions
  - Study question generation
  - Async processing for heavy AI tasks

- **Version Control**
  - Git-based version history
  - Branch management
  - Version restoration
  - Conflict resolution
  - Automated backups

- **Collaborative Editing**
  - Real-time collaboration
  - User presence tracking
  - Offline sync support
  - Conflict resolution

- **Export Options**
  - PDF export
  - HTML export
  - Markdown export
  - Batch export with ZIP archives
  - Background processing for large exports

- **Advanced Search**
  - Full-text search
  - Tag-based filtering
  - Elasticsearch integration
  - Search result highlighting
  - Optimized indexing

## Prerequisites

Before setting up the project, ensure you have the following installed:

- Python 3.8+
- MongoDB
- Redis (for caching and task queue)
- Rust (required for y-py package)
- wkhtmltopdf (for PDF export)
- Git
- Elasticsearch (for advanced search)

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd skript'd/backend
   ```

2. **Set Up Python Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install Rust (Required for y-py)**
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   source $HOME/.cargo/env
   ```

4. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set Up Environment Variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and configure:
   - MongoDB connection string
   - JWT secret key
   - OpenAI API key
   - Redis configuration
   - Other configuration variables

6. **Create Required Directories**
   ```bash
   mkdir -p data/git_repos
   mkdir -p backend/templates
   mkdir -p logs
   ```

7. **Start Required Services**
   ```bash
   # Start MongoDB
   sudo systemctl start mongodb

   # Start Redis
   sudo systemctl start redis-server

   # Start Elasticsearch
   sudo systemctl start elasticsearch
   ```

## Running the Application

1. **Start the Main Application**
   ```bash
   flask run
   ```

2. **Start Celery Worker (for background tasks)**
   ```bash
   celery -A tasks worker --loglevel=info
   ```

3. **Start Celery Beat (for scheduled tasks)**
   ```bash
   celery -A tasks beat --loglevel=info
   ```

4. **Start Flower (Celery monitoring, optional)**
   ```bash
   celery -A tasks flower
   ```

The API will be available at:
- Main API: `http://localhost:5000`
- API Documentation: `http://localhost:5000/api/docs`
- Flower Dashboard: `http://localhost:5555`
- Prometheus Metrics: `http://localhost:9090`

## Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_ai_service.py
```

## Monitoring and Metrics

### Prometheus Metrics
Available metrics include:
- HTTP request counts and durations
- Note operation counts
- AI request counts
- Collaboration session counts
- Export operation counts

### Grafana Dashboards
1. Import the provided dashboard templates
2. Access Grafana at `http://localhost:3000`
3. View metrics for:
   - API performance
   - Service health
   - User activity
   - System resources

## Caching

Redis is used for caching:
- Note content and metadata
- Search results
- AI responses
- User sessions

Cache configuration can be adjusted in `.env`:
```env
CACHE_TYPE=redis
CACHE_REDIS_URL=redis://localhost:6379/0
CACHE_DEFAULT_TIMEOUT=300
```

## Background Tasks

Celery is used for processing:
- Batch exports
- AI operations
- Repository backups
- Search index optimization
- Scheduled maintenance tasks

## API Documentation

Interactive API documentation is available at `/api/docs`, featuring:
- Endpoint descriptions
- Request/response schemas
- Authentication details
- Example requests

## Development

### Code Style
The project follows PEP 8 guidelines. Format code using:
```bash
black .
flake8
```

### Adding New Features
1. Create new service in `services/`
2. Add routes in `routes/`
3. Write tests in `tests/`
4. Update API documentation
5. Add metrics if needed

## Troubleshooting

### Common Issues

1. **Redis Connection Issues**
   - Verify Redis is running: `redis-cli ping`
   - Check Redis configuration in `.env`

2. **Celery Task Failures**
   - Check Flower dashboard for task status
   - Verify Redis broker connection
   - Check task logs in Flower

3. **MongoDB Connection Issues**
   - Verify MongoDB is running
   - Check connection string in `.env`
   - Verify database user permissions

4. **PDF Export Issues**
   - Verify wkhtmltopdf installation
   - Check `WKHTMLTOPDF_PATH` in `.env`

5. **Elasticsearch Issues**
   - Verify Elasticsearch is running
   - Check cluster health: `curl localhost:9200/_cluster/health`
   - Verify index settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[MIT License](LICENSE)
