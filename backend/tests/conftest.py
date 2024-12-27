import pytest
from flask_jwt_extended import create_access_token
from datetime import datetime
from bson import ObjectId
from app import create_app
from tests.config import TestConfig
from models import User, Note, Folder, Tag
from extensions import mongo

# Import all fixtures
from .fixtures import (
    test_users,
    test_folders_hierarchy,
    test_notes_with_versions,
    test_notes_with_tags,
    test_attachments,
    test_search_data,
    populated_db
)

@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    app = create_app(TestConfig)
    
    # Create test client
    with app.test_client() as client:
        with app.app_context():
            # Clear test database
            mongo.db.users.delete_many({})
            mongo.db.notes.delete_many({})
            mongo.db.folders.delete_many({})
            
            yield client

@pytest.fixture
def test_user(test_users):
    """Create a test user."""
    return test_users[0]

@pytest.fixture
def auth_headers(app, test_user):
    """Create authentication headers with JWT token."""
    with app.app_context():
        access_token = create_access_token(identity=str(test_user['_id']))
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'user_id': str(test_user['_id'])
        }
        return headers

@pytest.fixture
def test_folder(app, test_folders_hierarchy):
    """Create a test folder."""
    return test_folders_hierarchy['root']

@pytest.fixture
def test_note(app, test_notes_with_versions):
    """Create a test note."""
    return test_notes_with_versions['note']

@pytest.fixture
def test_tag(app, test_notes_with_tags):
    """Create a test tag."""
    return test_notes_with_tags['tags'][0]
