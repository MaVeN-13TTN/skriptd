from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask_apispec.extension import FlaskApiSpec
from marshmallow import Schema, fields

def init_docs(app):
    """Initialize API documentation."""
    app.config.update({
        'APISPEC_SPEC': APISpec(
            title='Skript\'d API',
            version='v1',
            plugins=[FlaskPlugin(), MarshmallowPlugin()],
            openapi_version='2.0',
            info={
                'description': 'API documentation for Skript\'d - A note-taking app for computer science students',
                'contact': {
                    'name': 'API Support',
                    'url': 'https://github.com/yourusername/skriptd'
                }
            }
        ),
        'APISPEC_SWAGGER_URL': '/api/docs/swagger.json',
        'APISPEC_SWAGGER_UI_URL': '/api/docs'
    })
    
    return FlaskApiSpec(app)

# Request/Response Schemas
class UserSchema(Schema):
    """User schema."""
    id = fields.Str(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class LoginSchema(Schema):
    """Login request schema."""
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class TokenSchema(Schema):
    """Token response schema."""
    access_token = fields.Str()
    token_type = fields.Str()

class NoteSchema(Schema):
    """Note schema."""
    id = fields.Str(dump_only=True)
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    folder_id = fields.Str(allow_none=True)
    tags = fields.List(fields.Str())
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class FolderSchema(Schema):
    """Folder schema."""
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    parent_id = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class TagSchema(Schema):
    """Tag schema."""
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class ErrorSchema(Schema):
    """Error response schema."""
    error = fields.Str()
    message = fields.Str()
    status_code = fields.Int()
