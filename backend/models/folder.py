from datetime import datetime
from bson import ObjectId

class Folder:
    def __init__(self, user_id, name, parent_id=None):
        self._id = ObjectId()
        self.user_id = ObjectId(user_id)
        self.name = name
        self.parent_id = ObjectId(parent_id) if parent_id else None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @staticmethod
    def from_dict(data):
        folder = Folder(
            user_id=data['user_id'],
            name=data['name'],
            parent_id=data.get('parent_id')
        )
        folder._id = data.get('_id', ObjectId())
        folder.created_at = data.get('created_at', datetime.utcnow())
        folder.updated_at = data.get('updated_at', datetime.utcnow())
        return folder

    def to_dict(self):
        return {
            '_id': str(self._id),
            'user_id': str(self.user_id),
            'name': self.name,
            'parent_id': str(self.parent_id) if self.parent_id else None,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def update(self, data):
        if 'name' in data:
            self.name = data['name']
        if 'parent_id' in data:
            self.parent_id = ObjectId(data['parent_id']) if data['parent_id'] else None
        self.updated_at = datetime.utcnow()
