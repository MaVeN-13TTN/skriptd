from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId

from models.note import Note
from errors import NotFoundError, AuthorizationError, ValidationError

notes_bp = Blueprint('notes', __name__)

@notes_bp.route('', methods=['POST'])
@jwt_required()
def create_note():
    """Create a new note."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('title') or not data.get('content'):
            raise ValidationError('Title and content are required')
        
        note = Note.create(
            request.mongo,
            user_id=user_id,
            title=data['title'],
            content=data['content'],
            folder_id=data.get('folder_id'),
            tags=data.get('tags', [])
        )
        
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
