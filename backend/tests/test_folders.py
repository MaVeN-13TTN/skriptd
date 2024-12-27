import pytest
import json
from bson import ObjectId
from extensions import mongo

def test_create_folder(app, auth_headers):
    """Test folder creation."""
    data = {
        'name': 'Test Folder',
        'description': 'A test folder'
    }
    
    response = app.post(
        '/api/folders',
        data=json.dumps(data),
        headers=auth_headers
    )
    
    assert response.status_code == 201
    assert response.json['name'] == data['name']
    assert response.json['description'] == data['description']
    
    # Verify folder was created in database
    with app.app_context():
        folder = mongo.db.folders.find_one({'_id': ObjectId(response.json['_id'])})
        assert folder is not None
        assert folder['name'] == data['name']

def test_get_folders(app, auth_headers, test_folder):
    """Test getting all folders."""
    response = app.get(
        '/api/folders',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0
    assert response.json[0]['name'] == test_folder['name']

def test_get_folder(app, auth_headers, test_folder):
    """Test getting a specific folder."""
    response = app.get(
        f'/api/folders/{test_folder["_id"]}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json['name'] == test_folder['name']

def test_update_folder(app, auth_headers, test_folder):
    """Test updating a folder."""
    data = {
        'name': 'Updated Folder',
        'description': 'Updated description'
    }
    
    response = app.put(
        f'/api/folders/{test_folder["_id"]}',
        data=json.dumps(data),
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json['name'] == data['name']
    assert response.json['description'] == data['description']

def test_delete_folder(app, auth_headers, test_folder):
    """Test deleting a folder."""
    response = app.delete(
        f'/api/folders/{test_folder["_id"]}',
        headers=auth_headers
    )
    
    assert response.status_code == 204
    
    # Verify folder was deleted
    with app.app_context():
        folder = mongo.db.folders.find_one({'_id': test_folder['_id']})
        assert folder is None

def test_create_nested_folder(app, auth_headers, test_folder):
    """Test creating a nested folder."""
    data = {
        'name': 'Nested Folder',
        'description': 'A nested test folder',
        'parent_id': str(test_folder['_id'])
    }
    
    response = app.post(
        '/api/folders',
        data=json.dumps(data),
        headers=auth_headers
    )
    
    assert response.status_code == 201
    assert response.json['name'] == data['name']
    assert response.json['parent_id'] == data['parent_id']

def test_get_folder_hierarchy(app, auth_headers, test_folder):
    """Test getting folder hierarchy."""
    response = app.get(
        '/api/folders/hierarchy',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert isinstance(response.json, list)
    # Verify the structure includes parent-child relationships
