from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime
from extensions import mongo

search_bp = Blueprint('search', __name__)

@search_bp.route('/', methods=['GET'])
@jwt_required()
def search():
    try:
        current_user_id = get_jwt_identity()
        query = request.args.get('q', '').strip()
        tag = request.args.get('tag')
        folder_id = request.args.get('folder_id')
        
        if not query and not tag and not folder_id:
            return jsonify({'error': 'No search criteria provided'}), 400
            
        # Build search query
        search_query = {'user_id': ObjectId(current_user_id)}
        
        if query:
            search_query['$or'] = [
                {'title': {'$regex': query, '$options': 'i'}},
                {'content': {'$regex': query, '$options': 'i'}}
            ]
            
        if tag:
            search_query['tags'] = tag
            
        if folder_id:
            search_query['folder_id'] = ObjectId(folder_id)
            
        # Execute search
        notes = list(mongo.db.notes.find(search_query).sort('updated_at', -1))
        
        # Format results
        for note in notes:
            note['_id'] = str(note['_id'])
            note['user_id'] = str(note['user_id'])
            if note.get('folder_id'):
                note['folder_id'] = str(note['folder_id'])
                
        return jsonify(notes), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@search_bp.route('/suggestions', methods=['GET'])
@jwt_required()
def get_suggestions():
    try:
        current_user_id = get_jwt_identity()
        prefix = request.args.get('q', '').strip()
        
        if not prefix:
            return jsonify([]), 200
            
        # Get tag suggestions
        tag_pipeline = [
            {'$match': {'user_id': ObjectId(current_user_id)}},
            {'$unwind': '$tags'},
            {'$match': {'tags': {'$regex': f'^{prefix}', '$options': 'i'}}},
            {'$group': {'_id': '$tags', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 5}
        ]
        
        tag_suggestions = list(mongo.db.notes.aggregate(tag_pipeline))
        
        # Get title suggestions
        title_pipeline = [
            {'$match': {
                'user_id': ObjectId(current_user_id),
                'title': {'$regex': f'^{prefix}', '$options': 'i'}
            }},
            {'$group': {'_id': '$title', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 5}
        ]
        
        title_suggestions = list(mongo.db.notes.aggregate(title_pipeline))
        
        suggestions = {
            'tags': [{'text': s['_id'], 'count': s['count']} for s in tag_suggestions],
            'titles': [{'text': s['_id'], 'count': s['count']} for s in title_suggestions]
        }
        
        return jsonify(suggestions), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
