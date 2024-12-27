from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime
from extensions import mongo

tags_bp = Blueprint('tags', __name__)

@tags_bp.route('/', methods=['GET'])
@jwt_required()
def get_tags():
    try:
        current_user_id = get_jwt_identity()
        
        # Get all unique tags from user's notes
        pipeline = [
            {'$match': {'user_id': ObjectId(current_user_id)}},
            {'$unwind': '$tags'},
            {'$group': {'_id': '$tags', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        
        tags = list(mongo.db.notes.aggregate(pipeline))
        
        # Format response
        formatted_tags = [{'name': tag['_id'], 'count': tag['count']} for tag in tags]
        
        return jsonify(formatted_tags), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tags_bp.route('/rename', methods=['PUT'])
@jwt_required()
def rename_tag():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('old_name') or not data.get('new_name'):
            return jsonify({'error': 'Old and new tag names are required'}), 400
            
        # Update all notes with the old tag
        result = mongo.db.notes.update_many(
            {
                'user_id': ObjectId(current_user_id),
                'tags': data['old_name']
            },
            {
                '$set': {
                    'tags.$[element]': data['new_name'],
                    'updated_at': datetime.utcnow()
                }
            },
            array_filters=[{'element': data['old_name']}]
        )
        
        return jsonify({
            'message': 'Tag renamed successfully',
            'modified_count': result.modified_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tags_bp.route('/delete', methods=['DELETE'])
@jwt_required()
def delete_tag():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('tag_name'):
            return jsonify({'error': 'Tag name is required'}), 400
            
        # Remove tag from all notes
        result = mongo.db.notes.update_many(
            {
                'user_id': ObjectId(current_user_id),
                'tags': data['tag_name']
            },
            {
                '$pull': {'tags': data['tag_name']},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        
        return jsonify({
            'message': 'Tag deleted successfully',
            'modified_count': result.modified_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
