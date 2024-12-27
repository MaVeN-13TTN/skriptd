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

# Test connection
with app.app_context():
    try:
        # Try to ping the database
        mongo.db.command('ping')
        print("Successfully connected to MongoDB!")
        
        # List all collections
        collections = mongo.db.list_collection_names()
        print("Available collections:", collections)
        
    except Exception as e:
        print("Failed to connect to MongoDB:", str(e))
