import pytest
import json
from bson import ObjectId
from extensions import mongo

def test_create_note(app, auth_headers, test_folder):
    """Test note creation."""
    data = {
        'title': 'New Note',
        'content': 'Note content',
        'folder_id': str(test_folder['_id']),
        'tags': ['test', 'new']
    }
    
    response = app.post(
        '/api/notes',
        data=json.dumps(data),
        headers=auth_headers
    )
    
    assert response.status_code == 201
    assert response.json['title'] == data['title']
    assert response.json['content'] == data['content']
    
    # Verify note was created in database
    with app.app_context():
        note = mongo.db.notes.find_one({'_id': ObjectId(response.json['_id'])})
        assert note is not None
        assert note['title'] == data['title']

def test_get_notes(app, auth_headers, test_note):
    """Test getting all notes."""
    response = app.get(
        '/api/notes',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0
    assert response.json[0]['title'] == test_note['title']

def test_get_note(app, auth_headers, test_note):
    """Test getting a specific note."""
    response = app.get(
        f'/api/notes/{test_note["_id"]}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json['title'] == test_note['title']
    assert response.json['content'] == test_note['content']

def test_update_note(app, auth_headers, test_note):
    """Test updating a note."""
    data = {
        'title': 'Updated Title',
        'content': 'Updated content'
    }
    
    response = app.put(
        f'/api/notes/{test_note["_id"]}',
        data=json.dumps(data),
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json['title'] == data['title']
    assert response.json['content'] == data['content']
    
    # Verify note was updated in database
    with app.app_context():
        note = mongo.db.notes.find_one({'_id': test_note['_id']})
        assert note['title'] == data['title']

def test_delete_note(app, auth_headers, test_note):
    """Test deleting a note."""
    response = app.delete(
        f'/api/notes/{test_note["_id"]}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    
    # Verify note was deleted from database
    with app.app_context():
        note = mongo.db.notes.find_one({'_id': test_note['_id']})
        assert note is None

def test_search_notes(app, auth_headers, test_note):
    """Test searching notes."""
    response = app.get(
        f'/api/notes?q={test_note["title"]}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0
    assert response.json[0]['title'] == test_note['title']

def test_get_notes_by_folder(app, auth_headers, test_note, test_folder):
    """Test getting notes in a folder."""
    response = app.get(
        f'/api/notes?folder_id={test_folder["_id"]}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0
    assert response.json[0]['folder_id'] == str(test_folder['_id'])
