import pytest
import io
import os
from bson import ObjectId
import json
from datetime import datetime
from extensions import mongo

@pytest.fixture
def test_file():
    """Create a test file."""
    return (io.BytesIO(b'Test file content'), 'test.txt')

@pytest.fixture
def test_image():
    """Create a test image."""
    return (io.BytesIO(b'Fake image content'), 'test.png')

@pytest.fixture
def test_attachment(app, test_user, test_note, test_file):
    """Create a test attachment."""
    file_content, filename = test_file
    attachment = {
        '_id': ObjectId(),
        'user_id': test_user['_id'],
        'note_id': test_note['_id'],
        'filename': 'stored_test.txt',
        'original_filename': filename,
        'path': os.path.join(app.application.config['UPLOAD_FOLDER'], 'stored_test.txt'),
        'size': len(file_content.getvalue()),
        'mime_type': 'text/plain',
        'file_hash': 'test_hash',
        'created_at': datetime.utcnow()
    }
    with app.app_context():
        mongo.db.attachments.insert_one(attachment)
    return attachment

def test_upload_file(app, auth_headers, test_note, test_file):
    """Test uploading a file."""
    file_content, filename = test_file
    data = {
        'file': (file_content, filename),
        'note_id': str(test_note['_id'])
    }
    
    response = app.post(
        '/api/attachments',
        headers={k: v for k, v in auth_headers.items() if k != 'Content-Type'},
        data=data,
        content_type='multipart/form-data'
    )
    assert response.status_code == 201
    result = json.loads(response.data)
    
    assert 'attachment' in result
    assert 'id' in result['attachment']
    assert 'filename' in result['attachment']
    assert result['message'] == 'File uploaded successfully'

def test_upload_invalid_file_type(app, auth_headers, test_note):
    """Test uploading a file with invalid type."""
    data = {
        'file': (io.BytesIO(b'Fake executable'), 'test.exe'),
        'note_id': str(test_note['_id'])
    }
    
    response = app.post(
        '/api/attachments',
        headers={k: v for k, v in auth_headers.items() if k != 'Content-Type'},
        data=data,
        content_type='multipart/form-data'
    )
    assert response.status_code == 400
    assert b'File type not allowed' in response.data

def test_upload_large_file(app, auth_headers, test_note):
    """Test uploading a file that exceeds size limit."""
    large_content = b'0' * (16 * 1024 * 1024 + 1)  # 16MB + 1 byte
    data = {
        'file': (io.BytesIO(large_content), 'large.txt'),
        'note_id': str(test_note['_id'])
    }
    
    response = app.post(
        '/api/attachments',
        headers={k: v for k, v in auth_headers.items() if k != 'Content-Type'},
        data=data,
        content_type='multipart/form-data'
    )
    assert response.status_code == 400
    assert b'File too large' in response.data

def test_download_file(app, auth_headers, test_attachment):
    """Test downloading a file."""
    response = app.get(
        f'/api/attachments/{test_attachment["_id"]}',
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.headers['Content-Type'] == test_attachment['mime_type']
    assert 'Content-Disposition' in response.headers

def test_delete_file(app, auth_headers, test_attachment):
    """Test deleting a file."""
    response = app.delete(
        f'/api/attachments/{test_attachment["_id"]}',
        headers=auth_headers
    )
    assert response.status_code == 200
    assert b'File deleted successfully' in response.data
    
    # Verify file is deleted from database
    with app.app_context():
        attachment = mongo.db.attachments.find_one({'_id': test_attachment['_id']})
        assert attachment is None

def test_get_note_attachments(app, auth_headers, test_note, test_attachment):
    """Test getting all attachments for a note."""
    response = app.get(
        f'/api/attachments/note/{test_note["_id"]}',
        headers=auth_headers
    )
    assert response.status_code == 200
    attachments = json.loads(response.data)
    
    assert len(attachments) == 1
    assert attachments[0]['filename'] == test_attachment['filename']
    assert attachments[0]['original_filename'] == test_attachment['original_filename']

def test_unauthorized_access(app, auth_headers, test_attachment):
    """Test unauthorized access to attachments."""
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
    
    # Try to download file
    response = app.get(
        f'/api/attachments/{test_attachment["_id"]}',
        headers=other_headers
    )
    assert response.status_code == 403

def test_file_not_found(app, auth_headers):
    """Test accessing non-existent file."""
    response = app.get(
        f'/api/attachments/{ObjectId()}',
        headers=auth_headers
    )
    assert response.status_code == 404

def test_upload_without_file(app, auth_headers, test_note):
    """Test upload request without file."""
    data = {
        'note_id': str(test_note['_id'])
    }
    
    response = app.post(
        '/api/attachments',
        headers={k: v for k, v in auth_headers.items() if k != 'Content-Type'},
        data=data,
        content_type='multipart/form-data'
    )
    assert response.status_code == 400
    assert b'No file provided' in response.data
