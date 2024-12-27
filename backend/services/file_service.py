import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
import mimetypes
import magic
import hashlib

class FileService:
    """Service for handling file operations."""
    
    ALLOWED_EXTENSIONS = {
        # Images
        'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp',
        # Documents
        'pdf', 'doc', 'docx', 'txt', 'md',
        # Code
        'py', 'js', 'jsx', 'ts', 'tsx', 'html', 'css', 'json', 'yaml', 'yml',
        # Archives
        'zip', 'tar', 'gz'
    }
    
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    
    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed."""
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in FileService.ALLOWED_EXTENSIONS
    
    @staticmethod
    def get_safe_filename(filename):
        """Generate a safe filename."""
        # Get file extension
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        # Generate unique filename
        safe_filename = secure_filename(filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        
        return f"{timestamp}_{unique_id}.{ext}"
    
    @staticmethod
    def get_file_hash(file_stream):
        """Calculate SHA-256 hash of file content."""
        sha256_hash = hashlib.sha256()
        for chunk in iter(lambda: file_stream.read(4096), b''):
            sha256_hash.update(chunk)
        file_stream.seek(0)  # Reset file pointer
        return sha256_hash.hexdigest()
    
    @staticmethod
    def validate_file_type(file_stream):
        """Validate file type using magic numbers."""
        mime = magic.Magic(mime=True)
        file_type = mime.from_buffer(file_stream.read(2048))
        file_stream.seek(0)  # Reset file pointer
        return file_type
    
    @staticmethod
    def save_file(file, user_id):
        """Save uploaded file."""
        if not file:
            raise ValueError('No file provided')
        
        # Validate file size
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        if size > FileService.MAX_FILE_SIZE:
            raise ValueError('File too large')
        
        # Get and validate filename
        filename = secure_filename(file.filename)
        if not FileService.allowed_file(filename):
            raise ValueError('File type not allowed')
        
        # Validate file type
        mime_type = FileService.validate_file_type(file)
        if not any(ext in mime_type for ext in ['text', 'image', 'application']):
            raise ValueError('Invalid file type')
        
        # Generate safe filename and path
        safe_filename = FileService.get_safe_filename(filename)
        user_upload_dir = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            str(user_id)
        )
        
        # Create user upload directory if it doesn't exist
        os.makedirs(user_upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(user_upload_dir, safe_filename)
        file.save(file_path)
        
        # Calculate file hash
        file_hash = FileService.get_file_hash(file)
        
        return {
            'filename': safe_filename,
            'original_filename': filename,
            'path': file_path,
            'size': size,
            'mime_type': mime_type,
            'hash': file_hash,
            'uploaded_at': datetime.utcnow()
        }
    
    @staticmethod
    def delete_file(file_path):
        """Delete file from storage."""
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    
    @staticmethod
    def get_file_info(file_path):
        """Get file information."""
        if not os.path.exists(file_path):
            return None
            
        stats = os.stat(file_path)
        filename = os.path.basename(file_path)
        
        return {
            'filename': filename,
            'path': file_path,
            'size': stats.st_size,
            'created_at': datetime.fromtimestamp(stats.st_ctime),
            'modified_at': datetime.fromtimestamp(stats.st_mtime),
            'mime_type': mimetypes.guess_type(file_path)[0]
        }
