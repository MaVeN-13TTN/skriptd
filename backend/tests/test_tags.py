import pytest
import json
from bson import ObjectId
from extensions import mongo

def test_create_tag(app, auth_headers):
    """Test tag creation."""
    data = {
        'name': 'TestTag',
        'color': '#FF5733'
    }
    
    response = app.post(
        '/api/tags',
        data=json.dumps(data),
        headers=auth_headers
    )
    
    assert response.status_code == 201
    assert response.json['name'] == data['name']
    assert response.json['color'] == data['color']
    
    # Verify tag was created in database
    with app.app_context():
        tag = mongo.db.tags.find_one({'_id': ObjectId(response.json['_id'])})
        assert tag is not None
        assert tag['name'] == data['name']

def test_get_tags(app, auth_headers, test_tag):
    """Test getting all tags."""
    response = app.get(
        '/api/tags',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0
    assert response.json[0]['name'] == test_tag['name']

def test_update_tag(app, auth_headers, test_tag):
    """Test updating a tag."""
    data = {
        'name': 'UpdatedTag',
        'color': '#33FF57'
    }
    
    response = app.put(
        f'/api/tags/{test_tag["_id"]}',
        data=json.dumps(data),
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json['name'] == data['name']
    assert response.json['color'] == data['color']

def test_delete_tag(app, auth_headers, test_tag):
    """Test deleting a tag."""
    response = app.delete(
        f'/api/tags/{test_tag["_id"]}',
        headers=auth_headers
    )
    
    assert response.status_code == 204
    
    # Verify tag was deleted
    with app.app_context():
        tag = mongo.db.tags.find_one({'_id': test_tag['_id']})
        assert tag is None

def test_get_notes_by_tag(app, auth_headers, test_tag, test_note):
    """Test getting notes by tag."""
    # First add tag to note
    with app.app_context():
        mongo.db.notes.update_one(
            {'_id': test_note['_id']},
            {'$push': {'tags': str(test_tag['_id'])}}
        )
    
    response = app.get(
        f'/api/tags/{test_tag["_id"]}/notes',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0
    assert str(test_note['_id']) in [note['_id'] for note in response.json]

def test_create_duplicate_tag(app, auth_headers, test_tag):
    """Test creating a tag with duplicate name."""
    data = {
        'name': test_tag['name'],
        'color': '#FF5733'
    }
    
    response = app.post(
        '/api/tags',
        data=json.dumps(data),
        headers=auth_headers
    )
    
    assert response.status_code == 409
