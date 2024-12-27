from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_mail import Mail

# Initialize extensions
mongo = PyMongo()
jwt = JWTManager()
socketio = SocketIO()
mail = Mail()
