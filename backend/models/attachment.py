from datetime import datetime
from bson import ObjectId

class Attachment:
    """Attachment model for files."""
    
    def __init__(
        self,
        user_id,
        filename,
        original_filename,
        path,
        size,
        mime_type,
        file_hash,
        note_id=None,
        _id=None
    ):
        self._id = _id or ObjectId()
        self.user_id = user_id
        self.note_id = note_id
        self.filename = filename
        self.original_filename = original_filename
        self.path = path
        self.size = size
        self.mime_type = mime_type
        self.file_hash = file_hash
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    @staticmethod
    def create(mongo, user_id, file_info, note_id=None):
        """Create a new attachment."""
        attachment = Attachment(
            user_id=user_id,
            filename=file_info['filename'],
            original_filename=file_info['original_filename'],
            path=file_info['path'],
            size=file_info['size'],
            mime_type=file_info['mime_type'],
            file_hash=file_info['hash'],
            note_id=note_id
        )
        
        mongo.db.attachments.insert_one(attachment.to_dict())
        return attachment
    
    @staticmethod
    def get_by_id(mongo, attachment_id):
        """Get attachment by ID."""
        data = mongo.db.attachments.find_one({'_id': ObjectId(attachment_id)})
        return Attachment.from_dict(data) if data else None
    
    @staticmethod
    def get_by_note(mongo, note_id):
        """Get all attachments for a note."""
        attachments = mongo.db.attachments.find({'note_id': ObjectId(note_id)})
        return [Attachment.from_dict(data) for data in attachments]
    
    @staticmethod
    def get_by_user(mongo, user_id):
        """Get all attachments for a user."""
        attachments = mongo.db.attachments.find({'user_id': ObjectId(user_id)})
        return [Attachment.from_dict(data) for data in attachments]
    
    def delete(self, mongo):
        """Delete attachment."""
        from services.file_service import FileService
        
        # Delete file from storage
        FileService.delete_file(self.path)
        
        # Delete from database
        mongo.db.attachments.delete_one({'_id': self._id})
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'note_id': self.note_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'path': self.path,
            'size': self.size,
            'mime_type': self.mime_type,
            'file_hash': self.file_hash,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def from_dict(data):
        """Create from dictionary."""
        if not data:
            return None
            
        return Attachment(
            user_id=data['user_id'],
            filename=data['filename'],
            original_filename=data['original_filename'],
            path=data['path'],
            size=data['size'],
            mime_type=data['mime_type'],
            file_hash=data['file_hash'],
            note_id=data.get('note_id'),
            _id=data['_id']
        )
