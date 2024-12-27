from datetime import datetime
from bson import ObjectId
import difflib

class NoteVersion:
    """Model for note versions."""
    
    def __init__(
        self,
        note_id,
        user_id,
        title,
        content,
        version_number,
        change_description=None,
        _id=None
    ):
        self._id = _id or ObjectId()
        self.note_id = note_id
        self.user_id = user_id
        self.title = title
        self.content = content
        self.version_number = version_number
        self.change_description = change_description
        self.created_at = datetime.utcnow()
    
    @staticmethod
    def create_version(mongo, note, change_description=None):
        """Create a new version of a note."""
        # Get the latest version number
        latest_version = mongo.db.note_versions.find_one(
            {'note_id': note._id},
            sort=[('version_number', -1)]
        )
        version_number = (latest_version['version_number'] + 1) if latest_version else 1
        
        # Create new version
        version = NoteVersion(
            note_id=note._id,
            user_id=note.user_id,
            title=note.title,
            content=note.content,
            version_number=version_number,
            change_description=change_description
        )
        
        mongo.db.note_versions.insert_one(version.to_dict())
        return version
    
    @staticmethod
    def get_versions(mongo, note_id):
        """Get all versions of a note."""
        versions = mongo.db.note_versions.find(
            {'note_id': ObjectId(note_id)},
            sort=[('version_number', -1)]
        )
        return [NoteVersion.from_dict(v) for v in versions]
    
    @staticmethod
    def get_version(mongo, note_id, version_number):
        """Get a specific version of a note."""
        version = mongo.db.note_versions.find_one({
            'note_id': ObjectId(note_id),
            'version_number': version_number
        })
        return NoteVersion.from_dict(version) if version else None
    
    def get_diff(self, other_version):
        """Get differences between this version and another version."""
        # Compare titles
        title_diff = list(difflib.unified_diff(
            [self.title],
            [other_version.title],
            lineterm=''
        ))
        
        # Compare contents
        content_diff = list(difflib.unified_diff(
            self.content.splitlines(),
            other_version.content.splitlines(),
            lineterm=''
        ))
        
        return {
            'title_diff': title_diff,
            'content_diff': content_diff
        }
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            '_id': self._id,
            'note_id': self.note_id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'version_number': self.version_number,
            'change_description': self.change_description,
            'created_at': self.created_at
        }
    
    @staticmethod
    def from_dict(data):
        """Create from dictionary."""
        if not data:
            return None
            
        return NoteVersion(
            note_id=data['note_id'],
            user_id=data['user_id'],
            title=data['title'],
            content=data['content'],
            version_number=data['version_number'],
            change_description=data.get('change_description'),
            _id=data['_id']
        )
