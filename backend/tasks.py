from celery import Celery
from celery.schedules import crontab
import os
from services.export import ExportService
from services.ai_service import AIService
from services.version_control import VersionControlService

celery = Celery(
    'skriptd',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
)

# Configure Celery
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3300,  # 55 minutes
)

# Export tasks
@celery.task(bind=True, name='tasks.export_notes')
def export_notes(self, note_ids, format, user_id):
    """Export multiple notes asynchronously."""
    try:
        export_service = ExportService()
        result = export_service.batch_export(note_ids, format, user_id)
        return {
            'status': 'success',
            'export_url': result['url']
        }
    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)

# AI tasks
@celery.task(bind=True, name='tasks.process_ai_requests')
def process_ai_requests(self, operation, content, **kwargs):
    """Process AI requests asynchronously."""
    try:
        ai_service = AIService()
        if operation == 'summarize':
            return ai_service.summarize_note(content, kwargs.get('max_length', 150))
        elif operation == 'explain_code':
            return ai_service.explain_code(content, kwargs.get('language'))
        elif operation == 'suggest_improvements':
            return ai_service.suggest_improvements(content, kwargs.get('language'))
        elif operation == 'study_questions':
            return ai_service.generate_study_questions(content)
    except Exception as e:
        self.retry(exc=e, countdown=30, max_retries=2)

# Version control tasks
@celery.task(name='tasks.backup_repositories')
def backup_repositories():
    """Backup all user repositories."""
    vc_service = VersionControlService()
    return vc_service.backup_all_repos()

# Scheduled tasks
@celery.task(name='tasks.cleanup_exports')
def cleanup_exports():
    """Clean up old exports."""
    export_service = ExportService()
    return export_service.cleanup_old_exports()

@celery.task(name='tasks.optimize_search_index')
def optimize_search_index():
    """Optimize Elasticsearch index."""
    from services.advanced_search import AdvancedSearch
    search_service = AdvancedSearch()
    return search_service.optimize_index()

# Schedule periodic tasks
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Cleanup exports daily at midnight
    sender.add_periodic_task(
        crontab(hour=0, minute=0),
        cleanup_exports.s()
    )
    
    # Backup repositories weekly
    sender.add_periodic_task(
        crontab(day_of_week=0, hour=1, minute=0),
        backup_repositories.s()
    )
    
    # Optimize search index weekly
    sender.add_periodic_task(
        crontab(day_of_week=0, hour=2, minute=0),
        optimize_search_index.s()
    )

# Example usage:
"""
# In your routes:
@notes_bp.route('/export/batch', methods=['POST'])
@jwt_required()
def batch_export():
    data = request.get_json()
    task = export_notes.delay(
        note_ids=data['note_ids'],
        format=data['format'],
        user_id=get_jwt_identity()
    )
    return jsonify({'task_id': task.id}), 202

@notes_bp.route('/task/<task_id>', methods=['GET'])
@jwt_required()
def get_task_status(task_id):
    task = celery.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Task is pending...'
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'result': task.result
        }
    else:
        response = {
            'state': task.state,
            'status': str(task.info)
        }
    return jsonify(response)
"""
