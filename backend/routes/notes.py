from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from io import BytesIO
import datetime

from models.note import Note
from errors import NotFoundError, AuthorizationError, ValidationError
from services.content_processor import ContentProcessor
from services.code_executor import CodeExecutor
from services.advanced_search import AdvancedSearch
from services.ai_service import AIService
from services.version_control import VersionControlService
from services.collaboration import CollaborationService
from services.export import ExportService

notes_bp = Blueprint('notes', __name__)

# Initialize services
content_processor = ContentProcessor()
code_executor = CodeExecutor()
advanced_search = AdvancedSearch(elasticsearch_url='http://localhost:9200')
ai_service = AIService()
version_control = VersionControlService(base_path='./data/git_repos')
collaboration = CollaborationService()
export_service = ExportService(templates_path='./templates')

@notes_bp.route('', methods=['POST'])
@jwt_required()
def create_note():
    """Create a new note with rich content processing."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('title') or not data.get('content'):
            raise ValidationError('Title and content are required')
        
        # Process content
        processed_content = content_processor.process_content(data['content'])
        
        # Create note with processed content
        note = Note.create(
            request.mongo,
            user_id=user_id,
            title=data['title'],
            content=data['content'],
            processed_content=processed_content,
            folder_id=data.get('folder_id'),
            tags=data.get('tags', [])
        )
        
        # Index note for search
        advanced_search.index_note(note.to_dict())
        
        return jsonify(note.to_dict()), 201
        
    except Exception as e:
        if isinstance(e, ValidationError):
            return jsonify({'error': str(e)}), 400
        return jsonify({'error': str(e)}), 500

@notes_bp.route('', methods=['GET'])
@jwt_required()
def get_notes():
    """Get all notes for the current user."""
    try:
        user_id = get_jwt_identity()
        folder_id = request.args.get('folder_id')
        tag = request.args.get('tag')
        
        # Get notes
        notes = Note.get_by_user(request.mongo, user_id, folder_id)
        
        # Filter by tag if specified
        if tag:
            notes = [note for note in notes if tag in note.tags]
        
        return jsonify([note.to_dict() for note in notes])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notes_bp.route('/<note_id>', methods=['GET'])
@jwt_required()
def get_note(note_id):
    """Get a specific note."""
    try:
        note = Note.get_by_id(request.mongo, note_id)
        if not note:
            raise NotFoundError('Note not found')
        
        # Check if user has access to the note
        user_id = get_jwt_identity()
        if str(note.user_id) != user_id:
            raise AuthorizationError('You do not have permission to access this note')
        
        return jsonify(note.to_dict())
        
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except AuthorizationError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notes_bp.route('/<note_id>', methods=['PUT'])
@jwt_required()
def update_note(note_id):
    """Update a note."""
    try:
        note = Note.get_by_id(request.mongo, note_id)
        if not note:
            raise NotFoundError('Note not found')
        
        # Check if user has access to the note
        user_id = get_jwt_identity()
        if str(note.user_id) != user_id:
            raise AuthorizationError('You do not have permission to modify this note')
        
        data = request.get_json()
        note.update(
            request.mongo,
            title=data.get('title'),
            content=data.get('content'),
            folder_id=data.get('folder_id'),
            tags=data.get('tags'),
            change_description=data.get('change_description')
        )
        
        # Process content
        processed_content = content_processor.process_content(note.content)
        note.update(request.mongo, processed_content=processed_content)
        
        # Index note for search
        advanced_search.index_note(note.to_dict())
        
        return jsonify(note.to_dict())
        
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except AuthorizationError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notes_bp.route('/<note_id>', methods=['DELETE'])
@jwt_required()
def delete_note(note_id):
    """Delete a note."""
    try:
        note = Note.get_by_id(request.mongo, note_id)
        if not note:
            raise NotFoundError('Note not found')
        
        # Check if user has access to the note
        user_id = get_jwt_identity()
        if str(note.user_id) != user_id:
            raise AuthorizationError('You do not have permission to delete this note')
        
        note.delete(request.mongo)
        return jsonify({'message': 'Note deleted successfully'})
        
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except AuthorizationError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notes_bp.route('/execute-code', methods=['POST'])
@jwt_required()
def execute_code():
    """Execute code snippet in sandbox environment."""
    try:
        data = request.get_json()
        if not data.get('code') or not data.get('language'):
            raise ValidationError('Code and language are required')
        
        result = code_executor.execute_code(
            code=data['code'],
            language=data['language'],
            timeout=data.get('timeout', 30)
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notes_bp.route('/validate-code', methods=['POST'])
@jwt_required()
def validate_code():
    """Validate code syntax."""
    try:
        data = request.get_json()
        if not data.get('code') or not data.get('language'):
            raise ValidationError('Code and language are required')
        
        result = code_executor.validate_code(
            code=data['code'],
            language=data['language']
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notes_bp.route('/export', methods=['POST'])
@jwt_required()
def export_note():
    """Export note in various formats."""
    try:
        data = request.get_json()
        note_id = data.get('note_id')
        format = data.get('format')
        
        if not note_id or not format:
            raise ValidationError('Note ID and format are required')
            
        note = Note.get_by_id(request.mongo, note_id)
        if not note:
            raise NotFoundError('Note not found')
            
        # Check if user has access to the note
        user_id = get_jwt_identity()
        if str(note.user_id) != user_id:
            raise AuthorizationError('You do not have permission to access this note')
        
        if format == 'pdf':
            content = content_processor.export_to_pdf(note.processed_content)
            return send_file(
                BytesIO(content),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"{note.title}.pdf"
            )
        elif format == 'markdown':
            content = content_processor.export_to_markdown(note.processed_content)
            return jsonify({'content': content})
        else:
            raise ValidationError('Unsupported export format')
            
    except Exception as e:
        if isinstance(e, (NotFoundError, AuthorizationError, ValidationError)):
            return jsonify({'error': str(e)}), 400
        return jsonify({'error': str(e)}), 500

@notes_bp.route('/ai/summarize', methods=['POST'])
@jwt_required()
def summarize_note():
    """Generate a summary of the note."""
    try:
        data = request.get_json()
        note_id = data.get('note_id')
        max_length = data.get('max_length', 150)
        
        note = Note.get_by_id(request.mongo, note_id)
        if not note:
            raise NotFoundError('Note not found')
        
        # Check access
        user_id = get_jwt_identity()
        if str(note.user_id) != user_id:
            raise AuthorizationError('You do not have permission to access this note')
        
        summary = ai_service.summarize_note(note.content, max_length)
        return jsonify({'summary': summary})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notes_bp.route('/ai/explain-code', methods=['POST'])
@jwt_required()
def explain_code():
    """Get AI explanation for code snippet."""
    try:
        data = request.get_json()
        if not data.get('code') or not data.get('language'):
            raise ValidationError('Code and language are required')
        
        explanation = ai_service.explain_code(
            code=data['code'],
            language=data['language']
        )
        return jsonify(explanation)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notes_bp.route('/ai/suggest-improvements', methods=['POST'])
@jwt_required()
def suggest_improvements():
    """Get AI suggestions for code improvements."""
    try:
        data = request.get_json()
        if not data.get('code') or not data.get('language'):
            raise ValidationError('Code and language are required')
        
        suggestions = ai_service.suggest_improvements(
            code=data['code'],
            language=data['language']
        )
        return jsonify(suggestions)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notes_bp.route('/ai/study-questions', methods=['POST'])
@jwt_required()
def generate_study_questions():
    """Generate study questions from note content."""
    try:
        data = request.get_json()
        note_id = data.get('note_id')
        
        note = Note.get_by_id(request.mongo, note_id)
        if not note:
            raise NotFoundError('Note not found')
        
        # Check access
        user_id = get_jwt_identity()
        if str(note.user_id) != user_id:
            raise AuthorizationError('You do not have permission to access this note')
        
        questions = ai_service.generate_study_questions(note.content)
        return jsonify({'questions': questions})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notes_bp.route('/version-control/init', methods=['POST'])
@jwt_required()
def init_version_control():
    """Initialize version control for user."""
    try:
        user_id = get_jwt_identity()
        result = version_control.init_user_repo(user_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notes_bp.route('/version-control/save', methods=['POST'])
@jwt_required()
def save_version():
    """Save current version of note."""
    try:
        data = request.get_json()
        note_id = data.get('note_id')
        
        note = Note.get_by_id(request.mongo, note_id)
        if not note:
            raise NotFoundError('Note not found')
        
        # Check access
        user_id = get_jwt_identity()
        if str(note.user_id) != user_id:
            raise AuthorizationError('You do not have permission to modify this note')
        
        result = version_control.save_note_version(
            user_id=user_id,
            note_id=note_id,
            content=note.to_dict()
        )
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notes_bp.route('/version-control/history/<note_id>', methods=['GET'])
@jwt_required()
def get_version_history(note_id):
    """Get version history of note."""
    try:
        note = Note.get_by_id(request.mongo, note_id)
        if not note:
            raise NotFoundError('Note not found')
        
        # Check access
        user_id = get_jwt_identity()
        if str(note.user_id) != user_id:
            raise AuthorizationError('You do not have permission to access this note')
        
        history = version_control.get_note_history(user_id, note_id)
        return jsonify({'history': history})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notes_bp.route('/version-control/restore', methods=['POST'])
@jwt_required()
def restore_version():
    """Restore note to specific version."""
    try:
        data = request.get_json()
        note_id = data.get('note_id')
        commit_hash = data.get('commit_hash')
        
        if not note_id or not commit_hash:
            raise ValidationError('Note ID and commit hash are required')
        
        note = Note.get_by_id(request.mongo, note_id)
        if not note:
            raise NotFoundError('Note not found')
        
        # Check access
        user_id = get_jwt_identity()
        if str(note.user_id) != user_id:
            raise AuthorizationError('You do not have permission to modify this note')
        
        result = version_control.restore_note_version(user_id, note_id, commit_hash)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notes_bp.route('/export/batch', methods=['POST'])
@jwt_required()
def batch_export():
    """Export multiple notes."""
    try:
        data = request.get_json()
        note_ids = data.get('note_ids', [])
        format = data.get('format')
        include_metadata = data.get('include_metadata', True)
        
        if not note_ids or not format:
            raise ValidationError('Note IDs and format are required')
        
        user_id = get_jwt_identity()
        notes = []
        
        # Collect all notes and verify access
        for note_id in note_ids:
            note = Note.get_by_id(request.mongo, note_id)
            if not note:
                continue
            
            if str(note.user_id) != user_id:
                continue
                
            notes.append(note.to_dict())
        
        if not notes:
            raise NotFoundError('No accessible notes found')
        
        # Generate export
        export_buffer = export_service.batch_export(notes, format, include_metadata)
        
        return send_file(
            export_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'notes_export_{datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.zip'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
