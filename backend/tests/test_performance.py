import pytest
import time
import concurrent.futures
from bson import ObjectId
import json
from datetime import datetime, timedelta

def test_note_creation_performance(app, auth_headers):
    """Test performance of note creation."""
    start_time = time.time()
    num_notes = 100
    
    # Create multiple notes
    for i in range(num_notes):
        data = {
            'title': f'Performance Test Note {i}',
            'content': f'Test content for note {i} with some additional text for realistic content size.',
            'tags': ['performance', 'test']
        }
        response = app.post(
            '/api/notes',
            data=json.dumps(data),
            headers=auth_headers
        )
        assert response.status_code == 201
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Assert creation time is within acceptable range (avg 50ms per note)
    assert duration < (num_notes * 0.05), f"Note creation too slow: {duration/num_notes}s per note"

def test_search_performance(app, auth_headers):
    """Test search performance with large dataset."""
    # First, create a large dataset
    num_notes = 1000
    search_term = "unique_search_term"
    
    with app.app_context():
        notes = [
            {
                'title': f'Performance Note {i}',
                'content': f'Content {i} {search_term if i % 10 == 0 else ""}',
                'user_id': ObjectId(auth_headers.get('user_id')),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            for i in range(num_notes)
        ]
        mongo.db.notes.insert_many(notes)
    
    start_time = time.time()
    response = app.get(
        f'/api/search?q={search_term}',
        headers=auth_headers
    )
    duration = time.time() - start_time
    
    assert response.status_code == 200
    # Search should complete within 500ms
    assert duration < 0.5, f"Search too slow: {duration}s"

def test_concurrent_note_access(app, auth_headers, test_note):
    """Test concurrent access to the same note."""
    num_concurrent = 50
    
    def access_note():
        return app.get(
            f'/api/notes/{test_note["_id"]}',
            headers=auth_headers
        )
    
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        futures = [executor.submit(access_note) for _ in range(num_concurrent)]
        responses = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    duration = time.time() - start_time
    
    # All requests should succeed
    assert all(response.status_code == 200 for response in responses)
    # Average response time should be under 100ms
    assert duration/num_concurrent < 0.1, f"Concurrent access too slow: {duration/num_concurrent}s per request"

def test_websocket_performance(socket_client, test_note):
    """Test WebSocket performance with rapid updates."""
    num_updates = 100
    start_time = time.time()
    
    # Join the note's room
    socket_client.emit('join', {'note_id': str(test_note['_id'])})
    
    # Send rapid updates
    for i in range(num_updates):
        edit_data = {
            'note_id': str(test_note['_id']),
            'content': f'Rapid update {i}',
            'cursor_position': i
        }
        socket_client.emit('edit', edit_data)
    
    # Wait for all updates to be processed
    time.sleep(1)
    received = socket_client.get_received()
    duration = time.time() - start_time
    
    # Should receive all updates plus join event
    assert len(received) > num_updates
    # Average processing time should be under 10ms per update
    assert duration/num_updates < 0.01, f"WebSocket updates too slow: {duration/num_updates}s per update"

def test_folder_hierarchy_performance(app, auth_headers):
    """Test performance of deep folder hierarchy."""
    # Create a deep folder structure
    depth = 10
    current_parent_id = None
    
    start_time = time.time()
    for i in range(depth):
        data = {
            'name': f'Depth {i}',
            'description': f'Folder at depth {i}',
            'parent_id': current_parent_id
        }
        response = app.post(
            '/api/folders',
            data=json.dumps(data),
            headers=auth_headers
        )
        assert response.status_code == 201
        current_parent_id = response.json['_id']
    
    # Test retrieving the full hierarchy
    response = app.get('/api/folders/hierarchy', headers=auth_headers)
    duration = time.time() - start_time
    
    assert response.status_code == 200
    # Hierarchy retrieval should be fast even with deep nesting
    assert duration < 0.5, f"Hierarchy retrieval too slow: {duration}s"

def test_rate_limiting(app, auth_headers):
    """Test rate limiting performance."""
    num_requests = 150  # Above the rate limit
    start_time = time.time()
    responses = []
    
    for i in range(num_requests):
        response = app.get('/api/notes', headers=auth_headers)
        responses.append(response.status_code)
    
    duration = time.time() - start_time
    
    # Should see some 429 (Too Many Requests) responses
    assert 429 in responses
    # Rate limiting should not add significant overhead
    assert duration/num_requests < 0.01, f"Rate limiting overhead too high: {duration/num_requests}s per request"
