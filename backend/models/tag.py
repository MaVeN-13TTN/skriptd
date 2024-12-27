from datetime import datetime
from bson import ObjectId

class Tag:
    def __init__(self, user_id, name):
        self._id = ObjectId()
        self.user_id = ObjectId(user_id)
        self.name = name
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @staticmethod
    def from_dict(data):
        tag = Tag(
            user_id=data['user_id'],
            name=data['name']
        )
        tag._id = data.get('_id', ObjectId())
        tag.created_at = data.get('created_at', datetime.utcnow())
        tag.updated_at = data.get('updated_at', datetime.utcnow())
        return tag

    def to_dict(self):
        return {
            '_id': str(self._id),
            'user_id': str(self.user_id),
            'name': self.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def update(self, data):
        if 'name' in data:
            self.name = data['name']
        self.updated_at = datetime.utcnow()
