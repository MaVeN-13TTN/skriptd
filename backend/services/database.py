from flask_pymongo import PyMongo
from bson import ObjectId

class Database:
    def __init__(self, app=None):
        self.mongo = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.mongo = PyMongo(app)

    def insert_one(self, collection, document):
        """Insert a single document into a collection."""
        return self.mongo.db[collection].insert_one(document)

    def find_one(self, collection, query):
        """Find a single document in a collection."""
        return self.mongo.db[collection].find_one(query)

    def find(self, collection, query=None, sort=None, limit=None):
        """Find documents in a collection with optional sorting and limit."""
        cursor = self.mongo.db[collection].find(query or {})
        if sort:
            cursor = cursor.sort(sort[0], sort[1])
        if limit:
            cursor = cursor.limit(limit)
        return cursor

    def update_one(self, collection, query, update):
        """Update a single document in a collection."""
        return self.mongo.db[collection].update_one(query, update)

    def update_many(self, collection, query, update):
        """Update multiple documents in a collection."""
        return self.mongo.db[collection].update_many(query, update)

    def delete_one(self, collection, query):
        """Delete a single document from a collection."""
        return self.mongo.db[collection].delete_one(query)

    def delete_many(self, collection, query):
        """Delete multiple documents from a collection."""
        return self.mongo.db[collection].delete_many(query)

    def aggregate(self, collection, pipeline):
        """Perform an aggregation pipeline on a collection."""
        return self.mongo.db[collection].aggregate(pipeline)

    def count_documents(self, collection, query):
        """Count documents in a collection that match a query."""
        return self.mongo.db[collection].count_documents(query)

    def create_index(self, collection, keys, **kwargs):
        """Create an index on a collection."""
        return self.mongo.db[collection].create_index(keys, **kwargs)

    def list_indexes(self, collection):
        """List all indexes on a collection."""
        return self.mongo.db[collection].list_indexes()

    def drop_collection(self, collection):
        """Drop a collection."""
        return self.mongo.db[collection].drop()
