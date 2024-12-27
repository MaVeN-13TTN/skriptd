import pytest
from bson import ObjectId
import json
from datetime import datetime, timedelta

def test_create_note_with_initial_version(app, auth_headers, test_user):
    """Test that creating a note automatically creates an initial version."""
    # Create a note
    response = app.post(
        '/api/notes',
        headers=auth_headers,
        json={
            'title': 'Test Note',
            'content': 'Initial content'
        }
    )
    assert response.status_code == 201
    note_data = json.loads(response.data)
    
    # Check version history
    response = app.get(
        f'/api/versions/notes/{note_data["_id"]}/versions',
        headers=auth_headers
    )
    assert response.status_code == 200
    versions = json.loads(response.data)
    
    assert len(versions) == 1
    assert versions[0]['version_number'] == 1
    assert versions[0]['title'] == 'Test Note'
    assert versions[0]['change_description'] == 'Initial version'

def test_update_note_creates_new_version(app, auth_headers, test_note):
    """Test that updating a note creates a new version."""
    # Update note
    response = app.put(
        f'/api/notes/{test_note["_id"]}',
        headers=auth_headers,
        json={
            'title': 'Updated Title',
            'content': 'Updated content',
            'change_description': 'Updated title and content'
        }
    )
    assert response.status_code == 200
    
    # Check version history
    response = app.get(
        f'/api/versions/notes/{test_note["_id"]}/versions',
        headers=auth_headers
    )
    assert response.status_code == 200
    versions = json.loads(response.data)
    
    assert len(versions) == 2
    assert versions[0]['version_number'] == 2
    assert versions[0]['title'] == 'Updated Title'
    assert versions[0]['change_description'] == 'Updated title and content'

def test_get_specific_version(app, auth_headers, test_note):
    """Test retrieving a specific version of a note."""
    # Create a new version by updating the note
    app.put(
        f'/api/notes/{test_note["_id"]}',
        headers=auth_headers,
        json={
            'title': 'Updated Title',
            'content': 'Updated content'
        }
    )
    
    # Get original version
    response = app.get(
        f'/api/versions/notes/{test_note["_id"]}/versions/1',
        headers=auth_headers
    )
    assert response.status_code == 200
    version = json.loads(response.data)
    
    assert version['version_number'] == 1
    assert version['title'] == test_note['title']
    assert version['content'] == test_note['content']

def test_revert_to_version(app, auth_headers, test_note):
    """Test reverting a note to a previous version."""
    # Create multiple versions
    versions = []
    for i in range(3):
        response = app.put(
            f'/api/notes/{test_note["_id"]}',
            headers=auth_headers,
            json={
                'title': f'Title {i+1}',
                'content': f'Content {i+1}'
            }
        )
        versions.append(json.loads(response.data))
    
    # Revert to version 2
    response = app.post(
        f'/api/versions/notes/{test_note["_id"]}/versions/2/revert',
        headers=auth_headers,
        json={'change_description': 'Reverted to version 2'}
    )
    assert response.status_code == 200
    
    # Check current note content
    response = app.get(
        f'/api/notes/{test_note["_id"]}',
        headers=auth_headers
    )
    note = json.loads(response.data)
    assert note['title'] == 'Title 1'
    assert note['content'] == 'Content 1'
    
    # Check version history
    response = app.get(
        f'/api/versions/notes/{test_note["_id"]}/versions',
        headers=auth_headers
    )
    versions = json.loads(response.data)
    assert len(versions) == 5  # Original + 3 updates + 1 revert
    assert versions[0]['change_description'] == 'Reverted to version 2'

def test_compare_versions(app, auth_headers, test_note):
    """Test comparing two versions of a note."""
    # Create a new version
    app.put(
        f'/api/notes/{test_note["_id"]}',
        headers=auth_headers,
        json={
            'title': 'Updated Title',
            'content': 'Updated content'
        }
    )
    
    # Compare versions
    response = app.get(
        f'/api/versions/notes/{test_note["_id"]}/versions/compare',
        headers=auth_headers,
        query_string={'v1': 1, 'v2': 2}
    )
    assert response.status_code == 200
    diff = json.loads(response.data)
    
    assert 'diff' in diff
    assert 'title_diff' in diff['diff']
    assert 'content_diff' in diff['diff']
    assert len(diff['diff']['title_diff']) > 0
    assert len(diff['diff']['content_diff']) > 0

def test_unauthorized_access(app, auth_headers, test_note):
    """Test unauthorized access to version history."""
    # Create different user's headers
    other_user = {
        '_id': ObjectId(),
        'username': 'other_user',
        'email': 'other@example.com'
    }
    with app.application.app_context():
        other_token = create_access_token(identity=str(other_user['_id']))
    other_headers = {
        'Authorization': f'Bearer {other_token}',
        'Content-Type': 'application/json'
    }
    
    # Try to access version history
    response = app.get(
        f'/api/versions/notes/{test_note["_id"]}/versions',
        headers=other_headers
    )
    assert response.status_code == 403
