import pytest
from flask_socketio import SocketIOTestClient
from bson import ObjectId
import json
import time

@pytest.fixture
def socket_client(app, auth_headers):
    """Create a Socket.IO test client."""
    token = auth_headers['Authorization'].split(' ')[1]
    client = SocketIOTestClient(
        app.application,
        app.application.socketio,
        auth={'token': token}
    )
    return client

def test_join_room(socket_client, test_note):
    """Test joining a note's editing room."""
    socket_client.emit('join', {'note_id': str(test_note['_id'])})
    received = socket_client.get_received()
    
    assert len(received) > 0
    assert received[0]['name'] == 'user_joined'
    assert 'user_id' in received[0]['args'][0]
    assert 'timestamp' in received[0]['args'][0]

def test_leave_room(socket_client, test_note):
    """Test leaving a note's editing room."""
    socket_client.emit('join', {'note_id': str(test_note['_id'])})
    socket_client.emit('leave', {'note_id': str(test_note['_id'])})
    received = socket_client.get_received()
    
    assert len(received) > 1
    assert received[1]['name'] == 'user_left'

def test_real_time_edit(socket_client, test_note):
    """Test real-time editing synchronization."""
    socket_client.emit('join', {'note_id': str(test_note['_id'])})
    
    edit_data = {
        'note_id': str(test_note['_id']),
        'content': 'Updated content',
        'cursor_position': 5
    }
    socket_client.emit('edit', edit_data)
    received = socket_client.get_received()
    
    assert len(received) > 1
    assert received[1]['name'] == 'edit'
    assert received[1]['args'][0]['content'] == edit_data['content']

def test_cursor_position(socket_client, test_note):
    """Test cursor position broadcasting."""
    socket_client.emit('join', {'note_id': str(test_note['_id'])})
    
    position_data = {
        'note_id': str(test_note['_id']),
        'position': 10
    }
    socket_client.emit('cursor_move', position_data)
    received = socket_client.get_received()
    
    assert len(received) > 1
    assert received[1]['name'] == 'cursor_position'
    assert received[1]['args'][0]['position'] == position_data['position']

def test_multiple_users_sync(app, auth_headers, test_note):
    """Test synchronization between multiple users."""
    # Create two socket clients
    token = auth_headers['Authorization'].split(' ')[1]
    client1 = SocketIOTestClient(
        app.application,
        app.application.socketio,
        auth={'token': token}
    )
    client2 = SocketIOTestClient(
        app.application,
        app.application.socketio,
        auth={'token': token}
    )
    
    # Both clients join the same room
    note_id = str(test_note['_id'])
    client1.emit('join', {'note_id': note_id})
    client2.emit('join', {'note_id': note_id})
    
    # Client 1 makes an edit
    edit_data = {
        'note_id': note_id,
        'content': 'Edit from client 1',
        'cursor_position': 5
    }
    client1.emit('edit', edit_data)
    
    # Check that client 2 received the edit
    received = client2.get_received()
    assert any(r['name'] == 'edit' and 
              r['args'][0]['content'] == edit_data['content'] 
              for r in received)

def test_connection_error_handling(socket_client):
    """Test error handling for invalid connection attempts."""
    # Try to join with invalid note_id
    socket_client.emit('join', {'note_id': 'invalid_id'})
    received = socket_client.get_received()
    
    assert len(received) > 0
    assert received[0]['name'] == 'error'
    assert 'message' in received[0]['args'][0]
