import pytest
from extensions import mongo
from bson import ObjectId
from flask import json

def test_register(app):
    """Test user registration."""
    data = {
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'SecurePass123!'
    }
    
    response = app.post(
        '/api/auth/register',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    assert 'access_token' in response.json
    
    # Verify user was created in database
    with app.application.app_context():
        user = mongo.db.users.find_one({'email': data['email']})
        assert user is not None
        assert user['username'] == data['username']

def test_register_duplicate_email(app, test_user):
    """Test registration with duplicate email."""
    data = {
        'username': 'another',
        'email': test_user['email'],
        'password': 'SecurePass123!'
    }
    
    response = app.post(
        '/api/auth/register',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 409
    assert 'error' in response.json

def test_login(app, test_user):
    """Test user login."""
    data = {
        'email': test_user['email'],
        'password': 'password123'
    }
    
    response = app.post(
        '/api/auth/login',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_login_invalid_credentials(app):
    """Test login with invalid credentials."""
    data = {
        'email': 'wrong@example.com',
        'password': 'wrongpass'
    }
    
    response = app.post(
        '/api/auth/login',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 401
    assert 'error' in response.json

def test_get_profile(app, auth_headers):
    """Test getting user profile."""
    response = app.get(
        '/api/auth/profile',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert 'username' in response.json
    assert 'email' in response.json

def test_get_profile_unauthorized(app):
    """Test getting profile without authentication."""
    response = app.get('/api/auth/profile')
    
    assert response.status_code == 401
    assert 'error' in response.json
