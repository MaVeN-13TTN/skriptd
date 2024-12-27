from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime
from extensions import mongo

folders_bp = Blueprint('folders', __name__)

@folders_bp.route('/', methods=['POST'])
@jwt_required()
def create_folder():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'Folder name is required'}), 400
            
        new_folder = {
            'user_id': ObjectId(current_user_id),
            'name': data['name'],
            'parent_id': ObjectId(data['parent_id']) if data.get('parent_id') else None,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = mongo.db.folders.insert_one(new_folder)
        new_folder['_id'] = str(result.inserted_id)
        new_folder['user_id'] = str(new_folder['user_id'])
        if new_folder.get('parent_id'):
            new_folder['parent_id'] = str(new_folder['parent_id'])
        
        return jsonify(new_folder), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@folders_bp.route('/', methods=['GET'])
@jwt_required()
def get_folders():
    try:
        current_user_id = get_jwt_identity()
        parent_id = request.args.get('parent_id')
        
        query = {'user_id': ObjectId(current_user_id)}
        if parent_id:
            query['parent_id'] = ObjectId(parent_id)
        else:
            query['parent_id'] = None  # Get root folders
            
        folders = list(mongo.db.folders.find(query).sort('name', 1))
        
        # Convert ObjectId to string
        for folder in folders:
            folder['_id'] = str(folder['_id'])
            folder['user_id'] = str(folder['user_id'])
            if folder.get('parent_id'):
                folder['parent_id'] = str(folder['parent_id'])
        
        return jsonify(folders), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@folders_bp.route('/<folder_id>', methods=['PUT'])
@jwt_required()
def update_folder(folder_id):
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'Folder name is required'}), 400
            
        # Validate folder ownership
        folder = mongo.db.folders.find_one({
            '_id': ObjectId(folder_id),
            'user_id': ObjectId(current_user_id)
        })
        
        if not folder:
            return jsonify({'error': 'Folder not found'}), 404
            
        # Update folder
        update_data = {
            'name': data['name'],
            'updated_at': datetime.utcnow()
        }
        
        if 'parent_id' in data:
            update_data['parent_id'] = ObjectId(data['parent_id']) if data['parent_id'] else None
            
        mongo.db.folders.update_one(
            {'_id': ObjectId(folder_id)},
            {'$set': update_data}
        )
        
        # Get updated folder
        updated_folder = mongo.db.folders.find_one({'_id': ObjectId(folder_id)})
        updated_folder['_id'] = str(updated_folder['_id'])
        updated_folder['user_id'] = str(updated_folder['user_id'])
        if updated_folder.get('parent_id'):
            updated_folder['parent_id'] = str(updated_folder['parent_id'])
        
        return jsonify(updated_folder), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@folders_bp.route('/<folder_id>', methods=['DELETE'])
@jwt_required()
def delete_folder(folder_id):
    try:
        current_user_id = get_jwt_identity()
        
        # Validate folder ownership
        folder = mongo.db.folders.find_one({
            '_id': ObjectId(folder_id),
            'user_id': ObjectId(current_user_id)
        })
        
        if not folder:
            return jsonify({'error': 'Folder not found'}), 404
            
        # Delete all notes in the folder
        mongo.db.notes.delete_many({'folder_id': ObjectId(folder_id)})
        
        # Delete all subfolders recursively
        def delete_subfolders(folder_id):
            subfolders = mongo.db.folders.find({'parent_id': ObjectId(folder_id)})
            for subfolder in subfolders:
                delete_subfolders(subfolder['_id'])
                mongo.db.folders.delete_one({'_id': subfolder['_id']})
        
        delete_subfolders(folder_id)
        
        # Delete the folder itself
        mongo.db.folders.delete_one({'_id': ObjectId(folder_id)})
        
        return jsonify({'message': 'Folder and its contents deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
