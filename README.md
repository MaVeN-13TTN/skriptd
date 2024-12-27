# Skript'd - Smart Note-Taking Application

Skript'd is a powerful note-taking application designed for developers and technical users. It features rich text editing, code snippet management, file attachments, and version history.

## Features

### Core Functionality
- 📝 Rich text editing with markdown support
- 🗂️ Hierarchical folder organization
- 🏷️ Tag-based organization
- 🔍 Full-text search
- 🔄 Real-time sync across devices

### Security
- 🔐 User authentication with JWT
- ✉️ Email verification
- 🔑 Secure password reset
- 🛡️ Rate limiting
- 📱 Device management

### Version Control
- 📚 Automatic version history
- 📊 Version comparison with diffs
- ⏮️ Version revert capability
- 📝 Change descriptions
- 🕒 Timestamp tracking

### File Management
- 📎 File attachments
- 🖼️ Image support
- 📄 Code file support
- 🔒 Secure file storage
- 🔍 File type validation

## Technology Stack

### Backend
- Python 3.12+
- Flask (Web Framework)
- MongoDB (Database)
- JWT (Authentication)
- Flask-Mail (Email Service)

### Frontend
- React.js
- Material-UI
- Redux
- React Router

## Getting Started

### Prerequisites
- Python 3.12 or higher
- MongoDB
- Node.js 16 or higher
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/skriptd.git
cd skriptd
```

2. Set up the Python virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt  # This installs all required dependencies
```

3. Configure environment variables:
```bash
cp .env.template .env
# Edit .env with your configuration
```

4. Set up the frontend:
```bash
cd ../frontend
npm install
```

### Configuration

Create a `.env` file in the backend directory with the following variables:

```env
# Server
FLASK_APP=app.py
FLASK_ENV=development
PORT=5000

# Database
MONGO_URI=mongodb://localhost:27017/skriptd

# Authentication
JWT_SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:3000

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# File Upload
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads
```

### Running the Application

1. Start MongoDB:
```bash
mongod
```

2. Start the backend server:
```bash
cd backend
source venv/bin/activate
flask run
```

3. Start the frontend development server:
```bash
cd frontend
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/verify-email` - Verify email
- `POST /api/auth/request-password-reset` - Request password reset
- `POST /api/auth/reset-password` - Reset password

### Note Endpoints
- `GET /api/notes` - Get all notes
- `POST /api/notes` - Create note
- `GET /api/notes/<id>` - Get note
- `PUT /api/notes/<id>` - Update note
- `DELETE /api/notes/<id>` - Delete note

### Version Endpoints
- `GET /api/versions/notes/<id>/versions` - Get version history
- `GET /api/versions/notes/<id>/versions/<num>` - Get specific version
- `POST /api/versions/notes/<id>/versions/<num>/revert` - Revert to version
- `GET /api/versions/notes/<id>/versions/compare` - Compare versions

### File Endpoints
- `POST /api/attachments` - Upload file
- `GET /api/attachments/<id>` - Download file
- `DELETE /api/attachments/<id>` - Delete file
- `GET /api/attachments/note/<id>` - Get note attachments

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors who have helped shape Skript'd
- Built with ❤️ using Flask and React
