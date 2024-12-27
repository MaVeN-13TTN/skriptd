from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime
from extensions import mongo, socketio

sync_bp = Blueprint('sync', __name__)

@socketio.on('join')
@jwt_required()
def on_join(data):
    """Join a note's editing room."""
    try:
        current_user_id = get_jwt_identity()
        note_id = data.get('note_id')
        
        if not note_id:
            return emit('error', {'message': 'Note ID is required'})
            
        # Verify user has access to the note
        note = mongo.db.notes.find_one({
            '_id': ObjectId(note_id),
            'user_id': ObjectId(current_user_id)
        })
        
        if not note:
            return emit('error', {'message': 'Note not found or access denied'})
            
        room = f'note_{note_id}'
        join_room(room)
        
        # Notify others in the room
        emit('user_joined', {
            'user_id': current_user_id,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room)
        
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('leave')
def on_leave(data):
    """Leave a note's editing room."""
    try:
        note_id = data.get('note_id')
        if note_id:
            room = f'note_{note_id}'
            leave_room(room)
            
            # Notify others in the room
            emit('user_left', {
                'user_id': get_jwt_identity(),
                'timestamp': datetime.utcnow().isoformat()
            }, room=room)
            
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('edit')
@jwt_required()
def on_edit(data):
    """Handle real-time edits to a note."""
    try:
        current_user_id = get_jwt_identity()
        note_id = data.get('note_id')
        changes = data.get('changes')
        
        if not note_id or not changes:
            return emit('error', {'message': 'Note ID and changes are required'})
            
        # Verify user has access to the note
        note = mongo.db.notes.find_one({
            '_id': ObjectId(note_id),
            'user_id': ObjectId(current_user_id)
        })
        
        if not note:
            return emit('error', {'message': 'Note not found or access denied'})
            
        # Apply changes to the note
        mongo.db.notes.update_one(
            {'_id': ObjectId(note_id)},
            {
                '$set': {
                    'content': changes.get('content'),
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        # Broadcast changes to all users in the room
        room = f'note_{note_id}'
        emit('change', {
            'note_id': note_id,
            'changes': changes,
            'user_id': current_user_id,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room, include_self=False)
        
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('cursor_move')
@jwt_required()
def on_cursor_move(data):
    """Broadcast cursor position to other users."""
    try:
        current_user_id = get_jwt_identity()
        note_id = data.get('note_id')
        position = data.get('position')
        
        if not note_id or position is None:
            return
            
        room = f'note_{note_id}'
        emit('cursor', {
            'user_id': current_user_id,
            'position': position,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room, include_self=False)
        
    except Exception as e:
        emit('error', {'message': str(e)})
