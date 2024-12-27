from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.attachment import Attachment
from extensions import mongo
from services.file_service import FileService
from errors import ValidationError, NotFoundError, AuthorizationError
from werkzeug.utils import secure_filename
import os

attachments_bp = Blueprint('attachments', __name__)

@attachments_bp.route('', methods=['POST'])
@jwt_required()
def upload_file():
    """Upload a file."""
    if 'file' not in request.files:
        raise ValidationError('No file provided')
    
    file = request.files['file']
    if file.filename == '':
        raise ValidationError('No file selected')
    
    # Get note ID if provided
    note_id = request.form.get('note_id')
    
    try:
        # Save file
        user_id = get_jwt_identity()
        file_info = FileService.save_file(file, user_id)
        
        # Create attachment record
        attachment = Attachment.create(
            mongo,
            user_id=user_id,
            file_info=file_info,
            note_id=note_id
        )
        
        return jsonify({
            'message': 'File uploaded successfully',
            'attachment': {
                'id': str(attachment._id),
                'filename': attachment.filename,
                'original_filename': attachment.original_filename,
                'size': attachment.size,
                'mime_type': attachment.mime_type,
                'created_at': attachment.created_at
            }
        }), 201
        
    except ValueError as e:
        raise ValidationError(str(e))

@attachments_bp.route('/<attachment_id>', methods=['GET'])
@jwt_required()
def download_file(attachment_id):
    """Download a file."""
    attachment = Attachment.get_by_id(mongo, attachment_id)
    if not attachment:
        raise NotFoundError('Attachment not found')
    
    # Check if user has access to the file
    user_id = get_jwt_identity()
    if str(attachment.user_id) != user_id:
        raise AuthorizationError('You do not have permission to access this file')
    
    if not os.path.exists(attachment.path):
        raise NotFoundError('File not found')
    
    return send_file(
        attachment.path,
        mimetype=attachment.mime_type,
        as_attachment=True,
        download_name=attachment.original_filename
    )

@attachments_bp.route('/<attachment_id>', methods=['DELETE'])
@jwt_required()
def delete_file(attachment_id):
    """Delete a file."""
    attachment = Attachment.get_by_id(mongo, attachment_id)
    if not attachment:
        raise NotFoundError('Attachment not found')
    
    # Check if user has access to the file
    user_id = get_jwt_identity()
    if str(attachment.user_id) != user_id:
        raise AuthorizationError('You do not have permission to delete this file')
    
    attachment.delete(mongo)
    return jsonify({'message': 'File deleted successfully'})

@attachments_bp.route('/note/<note_id>', methods=['GET'])
@jwt_required()
def get_note_attachments(note_id):
    """Get all attachments for a note."""
    attachments = Attachment.get_by_note(mongo, note_id)
    return jsonify([{
        'id': str(attachment._id),
        'filename': attachment.filename,
        'original_filename': attachment.original_filename,
        'size': attachment.size,
        'mime_type': attachment.mime_type,
        'created_at': attachment.created_at
    } for attachment in attachments])

@attachments_bp.route('', methods=['GET'])
@jwt_required()
def get_user_attachments():
    """Get all attachments for a user."""
    user_id = get_jwt_identity()
    attachments = Attachment.get_by_user(mongo, user_id)
    return jsonify([{
        'id': str(attachment._id),
        'filename': attachment.filename,
        'original_filename': attachment.original_filename,
        'size': attachment.size,
        'mime_type': attachment.mime_type,
        'created_at': attachment.created_at,
        'note_id': str(attachment.note_id) if attachment.note_id else None
    } for attachment in attachments])
