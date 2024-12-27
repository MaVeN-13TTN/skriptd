import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from extensions import mongo

@pytest.fixture
def test_users():
    """Create multiple test users."""
    users = [
        {
            '_id': ObjectId(),
            'username': f'testuser{i}',
            'email': f'test{i}@example.com',
            'password': 'hashed_password',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        for i in range(5)
    ]
    return users

@pytest.fixture
def test_folders_hierarchy():
    """Create a test folder hierarchy."""
    root_folder = {
        '_id': ObjectId(),
        'name': 'Root Folder',
        'description': 'Root level folder',
        'parent_id': None,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    subfolders = [
        {
            '_id': ObjectId(),
            'name': f'Subfolder {i}',
            'description': f'Subfolder level {i}',
            'parent_id': root_folder['_id'],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        for i in range(3)
    ]
    
    return {'root': root_folder, 'subfolders': subfolders}

@pytest.fixture
def test_notes_with_versions():
    """Create test notes with version history."""
    note = {
        '_id': ObjectId(),
        'title': 'Versioned Note',
        'content': 'Initial content',
        'current_version': 1,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    versions = [
        {
            '_id': ObjectId(),
            'note_id': note['_id'],
            'content': f'Content version {i}',
            'version_number': i,
            'change_description': f'Change {i}',
            'created_at': datetime.utcnow() - timedelta(hours=i)
        }
        for i in range(1, 4)
    ]
    
    return {'note': note, 'versions': versions}

@pytest.fixture
def test_notes_with_tags():
    """Create test notes with tags."""
    tags = [
        {
            '_id': ObjectId(),
            'name': f'Tag {i}',
            'color': f'#{"".join([str(i) for _ in range(6)])}'
        }
        for i in range(3)
    ]
    
    notes = [
        {
            '_id': ObjectId(),
            'title': f'Tagged Note {i}',
            'content': f'Content for note {i}',
            'tags': [str(tag['_id']) for tag in tags[:2]],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        for i in range(3)
    ]
    
    return {'notes': notes, 'tags': tags}

@pytest.fixture
def test_attachments():
    """Create test attachments."""
    return [
        {
            '_id': ObjectId(),
            'filename': f'test_file_{i}.txt',
            'content_type': 'text/plain',
            'size': 1024 * i,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        for i in range(3)
    ]

@pytest.fixture
def test_search_data(test_users, test_folders_hierarchy, test_notes_with_tags):
    """Create a comprehensive dataset for search testing."""
    user = test_users[0]
    root_folder = test_folders_hierarchy['root']
    notes = test_notes_with_tags['notes']
    tags = test_notes_with_tags['tags']
    
    # Add user_id and folder_id to notes
    for note in notes:
        note['user_id'] = user['_id']
        note['folder_id'] = root_folder['_id']
    
    return {
        'user': user,
        'folder': root_folder,
        'notes': notes,
        'tags': tags
    }

@pytest.fixture
def populated_db(app, test_search_data):
    """Populate the test database with a complete dataset."""
    with app.app_context():
        # Clear existing data
        mongo.db.users.delete_many({})
        mongo.db.folders.delete_many({})
        mongo.db.notes.delete_many({})
        mongo.db.tags.delete_many({})
        
        # Insert test data
        mongo.db.users.insert_one(test_search_data['user'])
        mongo.db.folders.insert_one(test_search_data['folder'])
        mongo.db.notes.insert_many(test_search_data['notes'])
        mongo.db.tags.insert_many(test_search_data['tags'])
        
    return test_search_data
