from .auth import auth_bp
from .notes import notes_bp
from .folders import folders_bp
from .tags import tags_bp
from .search import search_bp
from .sync import sync_bp

__all__ = ['auth_bp', 'notes_bp', 'folders_bp', 'tags_bp', 'search_bp', 'sync_bp']
