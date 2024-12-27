from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId

from models.note import Note
from errors import NotFoundError, AuthorizationError

versions_bp = Blueprint('versions', __name__)

@versions_bp.route('/notes/<note_id>/versions', methods=['GET'])
@jwt_required()
def get_note_versions(note_id):
    """Get version history of a note."""
    note = Note.get_by_id(request.mongo, note_id)
    if not note:
        raise NotFoundError('Note not found')
    
    # Check if user has access to the note
    user_id = get_jwt_identity()
    if str(note.user_id) != user_id:
        raise AuthorizationError('You do not have permission to access this note')
    
    versions = note.get_version_history(request.mongo)
    return jsonify([{
        'version_number': v.version_number,
        'title': v.title,
        'change_description': v.change_description,
        'created_at': v.created_at
    } for v in versions])

@versions_bp.route('/notes/<note_id>/versions/<int:version_number>', methods=['GET'])
@jwt_required()
def get_note_version(note_id, version_number):
    """Get a specific version of a note."""
    note = Note.get_by_id(request.mongo, note_id)
    if not note:
        raise NotFoundError('Note not found')
    
    # Check if user has access to the note
    user_id = get_jwt_identity()
    if str(note.user_id) != user_id:
        raise AuthorizationError('You do not have permission to access this note')
    
    version = note.get_version(request.mongo, version_number)
    if not version:
        raise NotFoundError('Version not found')
    
    return jsonify({
        'version_number': version.version_number,
        'title': version.title,
        'content': version.content,
        'change_description': version.change_description,
        'created_at': version.created_at
    })

@versions_bp.route('/notes/<note_id>/versions/<int:version_number>/revert', methods=['POST'])
@jwt_required()
def revert_to_version(note_id, version_number):
    """Revert note to a specific version."""
    note = Note.get_by_id(request.mongo, note_id)
    if not note:
        raise NotFoundError('Note not found')
    
    # Check if user has access to the note
    user_id = get_jwt_identity()
    if str(note.user_id) != user_id:
        raise AuthorizationError('You do not have permission to modify this note')
    
    change_description = request.json.get('change_description')
    note.revert_to_version(request.mongo, version_number, change_description)
    
    return jsonify({
        'message': f'Note reverted to version {version_number}',
        'current_version': note.current_version
    })

@versions_bp.route('/notes/<note_id>/versions/compare', methods=['GET'])
@jwt_required()
def compare_versions(note_id):
    """Compare two versions of a note."""
    note = Note.get_by_id(request.mongo, note_id)
    if not note:
        raise NotFoundError('Note not found')
    
    # Check if user has access to the note
    user_id = get_jwt_identity()
    if str(note.user_id) != user_id:
        raise AuthorizationError('You do not have permission to access this note')
    
    # Get version numbers from query parameters
    try:
        v1 = int(request.args.get('v1'))
        v2 = int(request.args.get('v2'))
    except (TypeError, ValueError):
        raise ValidationError('Invalid version numbers')
    
    diff = note.compare_versions(request.mongo, v1, v2)
    return jsonify({
        'v1': v1,
        'v2': v2,
        'diff': diff
    })
