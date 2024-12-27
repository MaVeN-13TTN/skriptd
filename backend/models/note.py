from datetime import datetime
from bson import ObjectId
from models.note_version import NoteVersion

class Note:
    """Note model."""
    
    def __init__(
        self,
        user_id,
        title,
        content,
        folder_id=None,
        tags=None,
        attachments=None,
        current_version=1,
        _id=None
    ):
        self._id = _id or ObjectId()
        self.user_id = ObjectId(user_id)
        self.title = title
        self.content = content
        self.folder_id = ObjectId(folder_id) if folder_id else None
        self.tags = tags or []
        self.attachments = attachments or []
        self.current_version = current_version
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    @staticmethod
    def create(mongo, user_id, title, content, folder_id=None, tags=None):
        """Create a new note."""
        note = Note(
            user_id=user_id,
            title=title,
            content=content,
            folder_id=folder_id,
            tags=tags
        )
        mongo.db.notes.insert_one(note.to_dict())
        
        # Create initial version
        NoteVersion.create_version(mongo, note, "Initial version")
        
        return note
    
    def update(self, mongo, title=None, content=None, folder_id=None, tags=None, change_description=None):
        """Update note and create new version."""
        updates = {}
        content_changed = False
        
        if title is not None and title != self.title:
            self.title = title
            updates['title'] = title
            content_changed = True
        
        if content is not None and content != self.content:
            self.content = content
            updates['content'] = content
            content_changed = True
        
        if folder_id is not None:
            self.folder_id = ObjectId(folder_id) if folder_id else None
            updates['folder_id'] = folder_id
        
        if tags is not None:
            self.tags = tags
            updates['tags'] = tags
        
        if content_changed:
            # Increment version number
            self.current_version += 1
            updates['current_version'] = self.current_version
            
            # Create new version
            NoteVersion.create_version(mongo, self, change_description)
        
        self.updated_at = datetime.utcnow()
        updates['updated_at'] = self.updated_at
        
        if updates:
            mongo.db.notes.update_one(
                {'_id': self._id},
                {'$set': updates}
            )
    
    def revert_to_version(self, mongo, version_number, change_description=None):
        """Revert note to a specific version."""
        version = NoteVersion.get_version(mongo, self._id, version_number)
        if not version:
            raise ValueError(f"Version {version_number} not found")
        
        # Update note with version content
        self.update(
            mongo,
            title=version.title,
            content=version.content,
            change_description=change_description or f"Reverted to version {version_number}"
        )
    
    def get_version_history(self, mongo):
        """Get version history of the note."""
        return NoteVersion.get_versions(mongo, self._id)
    
    def get_version(self, mongo, version_number):
        """Get specific version of the note."""
        return NoteVersion.get_version(mongo, self._id, version_number)
    
    def compare_versions(self, mongo, version1_number, version2_number):
        """Compare two versions of the note."""
        v1 = self.get_version(mongo, version1_number)
        v2 = self.get_version(mongo, version2_number)
        
        if not v1 or not v2:
            raise ValueError("One or both versions not found")
        
        return v1.get_diff(v2)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            '_id': str(self._id),
            'user_id': str(self.user_id),
            'title': self.title,
            'content': self.content,
            'folder_id': str(self.folder_id) if self.folder_id else None,
            'tags': self.tags,
            'attachments': self.attachments,
            'current_version': self.current_version,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def from_dict(data):
        """Create from dictionary."""
        if not data:
            return None
            
        return Note(
            user_id=data['user_id'],
            title=data['title'],
            content=data['content'],
            folder_id=data.get('folder_id'),
            tags=data.get('tags', []),
            attachments=data.get('attachments', []),
            current_version=data.get('current_version', 1),
            _id=data['_id']
        )
