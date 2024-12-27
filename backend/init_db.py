from flask import Flask
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure MongoDB
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

def init_collections():
    with app.app_context():
        # Create collections with validators
        try:
            # Users collection
            if "users" not in mongo.db.list_collection_names():
                mongo.db.create_collection("users")
                mongo.db.users.create_index("email", unique=True)
                print("Created users collection")

            # Notes collection
            if "notes" not in mongo.db.list_collection_names():
                mongo.db.create_collection("notes")
                mongo.db.notes.create_index([("user_id", 1), ("title", 1)])
                print("Created notes collection")

            # Folders collection
            if "folders" not in mongo.db.list_collection_names():
                mongo.db.create_collection("folders")
                mongo.db.folders.create_index([("user_id", 1), ("name", 1)])
                print("Created folders collection")

            # Tags collection
            if "tags" not in mongo.db.list_collection_names():
                mongo.db.create_collection("tags")
                mongo.db.tags.create_index([("user_id", 1), ("name", 1)], unique=True)
                print("Created tags collection")

            # Note versions collection
            if "note_versions" not in mongo.db.list_collection_names():
                mongo.db.create_collection("note_versions")
                mongo.db.note_versions.create_index([("note_id", 1), ("version", 1)])
                print("Created note_versions collection")

            # Attachments collection
            if "attachments" not in mongo.db.list_collection_names():
                mongo.db.create_collection("attachments")
                mongo.db.attachments.create_index([("note_id", 1)])
                print("Created attachments collection")

            print("\nDatabase initialization completed successfully!")
            
            # Show all collections
            collections = mongo.db.list_collection_names()
            print("\nAvailable collections:", collections)

        except Exception as e:
            print(f"Error initializing database: {str(e)}")

if __name__ == "__main__":
    init_collections()
