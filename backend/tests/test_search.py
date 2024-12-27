import pytest
import json
from bson import ObjectId
from extensions import mongo

def test_basic_search(app, auth_headers, test_note):
    """Test basic search functionality."""
    response = app.get(
        f'/api/search?q={test_note["title"]}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0
    assert response.json[0]['title'] == test_note['title']

def test_content_search(app, auth_headers, test_note):
    """Test searching in note content."""
    response = app.get(
        f'/api/search?q={test_note["content"]}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0
    assert response.json[0]['content'] == test_note['content']

def test_tag_search(app, auth_headers, test_note, test_tag):
    """Test searching by tag."""
    # Add tag to note
    with app.app_context():
        mongo.db.notes.update_one(
            {'_id': test_note['_id']},
            {'$push': {'tags': str(test_tag['_id'])}}
        )
    
    response = app.get(
        f'/api/search?tag={test_tag["name"]}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0
    assert str(test_note['_id']) in [note['_id'] for note in response.json]

def test_folder_search(app, auth_headers, test_note, test_folder):
    """Test searching within a folder."""
    response = app.get(
        f'/api/search?q={test_note["title"]}&folder={test_folder["_id"]}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert all(note['folder_id'] == str(test_folder['_id']) for note in response.json)

def test_date_range_search(app, auth_headers, test_note):
    """Test searching by date range."""
    response = app.get(
        '/api/search?start_date=2024-01-01&end_date=2024-12-31',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_combined_search(app, auth_headers, test_note, test_tag, test_folder):
    """Test combined search with multiple parameters."""
    # Add tag to note
    with app.app_context():
        mongo.db.notes.update_one(
            {'_id': test_note['_id']},
            {'$push': {'tags': str(test_tag['_id'])}}
        )
    
    response = app.get(
        f'/api/search?q={test_note["title"]}&tag={test_tag["name"]}&folder={test_folder["_id"]}',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_search_pagination(app, auth_headers):
    """Test search result pagination."""
    # Create multiple notes
    for i in range(15):
        with app.app_context():
            mongo.db.notes.insert_one({
                'title': f'Test Note {i}',
                'content': 'Test content',
                'user_id': ObjectId(auth_headers['user_id'])
            })
    
    response = app.get(
        '/api/search?q=Test&page=1&per_page=10',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert 'items' in response.json
    assert 'total' in response.json
    assert 'page' in response.json
    assert len(response.json['items']) == 10

def test_invalid_search_params(app, auth_headers):
    """Test search with invalid parameters."""
    response = app.get(
        '/api/search?invalid_param=value',
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert 'error' in response.json
