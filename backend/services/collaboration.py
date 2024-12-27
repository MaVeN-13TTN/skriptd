from typing import Dict, List, Optional, Set
import asyncio
import json
from datetime import datetime
import websockets
from operational_transform import Server as OTServer
from operational_transform.text_operation import TextOperation
import y_py as Y

class CollaborationService:
    """Service for handling real-time collaborative editing."""
    
    def __init__(self):
        self.active_documents: Dict[str, 'Document'] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # document_id -> set of user_ids
        self.ot_servers: Dict[str, OTServer] = {}
        
    async def handle_connection(self, websocket, document_id: str, user_id: str):
        """Handle a new WebSocket connection for collaborative editing."""
        try:
            # Initialize document if it doesn't exist
            if document_id not in self.active_documents:
                self.active_documents[document_id] = Document(document_id)
                self.ot_servers[document_id] = OTServer()
            
            # Add user to document's connections
            if document_id not in self.user_connections:
                self.user_connections[document_id] = set()
            self.user_connections[document_id].add(user_id)
            
            # Notify others about new user
            await self._broadcast_presence(document_id, user_id, 'joined')
            
            try:
                async for message in websocket:
                    await self._handle_message(websocket, message, document_id, user_id)
            finally:
                # Clean up when user disconnects
                self.user_connections[document_id].remove(user_id)
                await self._broadcast_presence(document_id, user_id, 'left')
                
                # Clean up document if no users left
                if not self.user_connections[document_id]:
                    del self.active_documents[document_id]
                    del self.ot_servers[document_id]
                    del self.user_connections[document_id]
                    
        except Exception as e:
            print(f"Error in handle_connection: {str(e)}")
    
    async def _handle_message(self, websocket, message: str, document_id: str, user_id: str):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'operation':
                # Handle text operation
                operation = TextOperation.from_json(data['operation'])
                server = self.ot_servers[document_id]
                
                # Transform and apply operation
                transformed_op = server.receive_operation(data['revision'], operation)
                self.active_documents[document_id].apply_operation(transformed_op)
                
                # Broadcast to other users
                await self._broadcast_operation(document_id, user_id, transformed_op, server.revision)
                
            elif message_type == 'cursor':
                # Handle cursor position update
                await self._broadcast_cursor(document_id, user_id, data['position'])
                
            elif message_type == 'sync':
                # Send current document state
                await self._send_sync_data(websocket, document_id)
                
        except Exception as e:
            print(f"Error handling message: {str(e)}")
            await websocket.send(json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def _broadcast_operation(
        self,
        document_id: str,
        sender_id: str,
        operation: TextOperation,
        revision: int
    ):
        """Broadcast operation to all users except sender."""
        message = json.dumps({
            'type': 'operation',
            'sender': sender_id,
            'operation': operation.to_json(),
            'revision': revision
        })
        
        await self._broadcast(document_id, message, exclude_user=sender_id)
    
    async def _broadcast_cursor(self, document_id: str, user_id: str, position: int):
        """Broadcast cursor position to all users."""
        message = json.dumps({
            'type': 'cursor',
            'user': user_id,
            'position': position
        })
        
        await self._broadcast(document_id, message)
    
    async def _broadcast_presence(self, document_id: str, user_id: str, event: str):
        """Broadcast user presence events."""
        message = json.dumps({
            'type': 'presence',
            'user': user_id,
            'event': event,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        await self._broadcast(document_id, message)
    
    async def _send_sync_data(self, websocket, document_id: str):
        """Send current document state to client."""
        document = self.active_documents[document_id]
        server = self.ot_servers[document_id]
        
        sync_data = {
            'type': 'sync',
            'content': document.content,
            'revision': server.revision,
            'users': list(self.user_connections[document_id])
        }
        
        await websocket.send(json.dumps(sync_data))
    
    async def _broadcast(self, document_id: str, message: str, exclude_user: Optional[str] = None):
        """Broadcast message to all users in a document."""
        tasks = []
        for user_id in self.user_connections[document_id]:
            if user_id != exclude_user:
                tasks.append(self._send_to_user(user_id, message))
        
        if tasks:
            await asyncio.gather(*tasks)
    
    async def _send_to_user(self, user_id: str, message: str):
        """Send message to specific user."""
        # This is a placeholder - actual implementation would depend on your WebSocket management
        pass


class Document:
    """Represents a collaborative document."""
    
    def __init__(self, document_id: str, initial_content: str = ""):
        self.document_id = document_id
        self.content = initial_content
        self.ydoc = Y.YDoc()
        self.ytext = self.ydoc.get_text("content")
        
        # Initialize with initial content
        if initial_content:
            self.ytext.insert(0, initial_content)
    
    def apply_operation(self, operation: TextOperation):
        """Apply a text operation to the document."""
        # Apply to string content
        self.content = operation.apply(self.content)
        
        # Apply to Yjs document
        with self.ydoc.begin_transaction() as txn:
            if operation.ops:
                for op in operation.ops:
                    if isinstance(op, str):
                        # Insert operation
                        self.ytext.insert(txn, len(self.content), op)
                    elif isinstance(op, int):
                        if op > 0:
                            # Retain operation
                            pass
                        else:
                            # Delete operation
                            self.ytext.delete(txn, len(self.content), abs(op))
    
    def get_content(self) -> str:
        """Get current document content."""
        return self.content
    
    def create_update(self) -> bytes:
        """Create a Yjs update message."""
        return Y.encode_state_vector(self.ydoc)
    
    def apply_update(self, update: bytes):
        """Apply a Yjs update."""
        Y.apply_update(self.ydoc, update)
