# Backend-Frontend Alignment Guide

This document outlines how the backend services and APIs align with frontend requirements and components.

## 1. Core Features Alignment

### Authentication & User Management
Backend Components:
- `routes/auth.py`: Authentication endpoints
- `services/email_service.py`: Email notifications

Required Frontend Components:
```typescript
// src/components/auth/
- Login.tsx
- Register.tsx
- ForgotPassword.tsx
- ResetPassword.tsx
- UserProfile.tsx
```

API Endpoints:
```typescript
POST /api/auth/register
POST /api/auth/login
POST /api/auth/refresh
POST /api/auth/forgot-password
POST /api/auth/reset-password
GET /api/auth/profile
```

### Note Management
Backend Components:
- `routes/notes.py`: Note CRUD operations
- `services/content_processor.py`: Note content processing
- `services/file_service.py`: File handling

Required Frontend Components:
```typescript
// src/components/notes/
- NoteEditor.tsx
- NoteList.tsx
- NoteViewer.tsx
- NoteTags.tsx
- NoteAttachments.tsx
```

API Endpoints:
```typescript
GET /api/notes
POST /api/notes
GET /api/notes/:id
PUT /api/notes/:id
DELETE /api/notes/:id
POST /api/notes/:id/attachments
```

### AI Features
Backend Components:
- `services/ai_service.py`: AI processing
- `tasks.py`: Async task processing

Required Frontend Components:
```typescript
// src/components/ai/
- NoteSummarizer.tsx
- CodeExplainer.tsx
- ImprovementSuggestions.tsx
- StudyQuestions.tsx
- AIProgress.tsx
```

API Endpoints:
```typescript
POST /api/notes/ai/summarize
POST /api/notes/ai/explain-code
POST /api/notes/ai/suggest-improvements
POST /api/notes/ai/study-questions
GET /api/tasks/:taskId/status
```

### Version Control
Backend Components:
- `routes/versions.py`: Version control endpoints
- `services/version_control.py`: Git operations

Required Frontend Components:
```typescript
// src/components/version-control/
- VersionHistory.tsx
- BranchManager.tsx
- DiffViewer.tsx
- MergeConflictResolver.tsx
```

API Endpoints:
```typescript
GET /api/notes/:id/versions
POST /api/notes/:id/versions
POST /api/notes/:id/branches
GET /api/notes/:id/branches
POST /api/notes/:id/merge
```

### Collaborative Editing
Backend Components:
- `routes/sync.py`: Sync endpoints
- `services/collaboration.py`: Real-time collaboration

Required Frontend Components:
```typescript
// src/components/collaboration/
- CollaborativeEditor.tsx
- UserPresence.tsx
- ConflictResolver.tsx
- SyncStatus.tsx
```

WebSocket Endpoints:
```typescript
ws://api/collaboration/note/:id
ws://api/collaboration/presence/:id
```

### Search & Organization
Backend Components:
- `routes/search.py`: Search endpoints
- `services/advanced_search.py`: Search functionality
- `routes/folders.py`: Folder management
- `routes/tags.py`: Tag management

Required Frontend Components:
```typescript
// src/components/organization/
- SearchBar.tsx
- SearchResults.tsx
- FolderTree.tsx
- TagManager.tsx
- FilterPanel.tsx
```

API Endpoints:
```typescript
GET /api/search
GET /api/folders
POST /api/folders
GET /api/tags
POST /api/tags
```

## 2. State Management Requirements

### Frontend State Structure
```typescript
interface AppState {
  auth: {
    user: User | null;
    token: string | null;
    isLoading: boolean;
  };
  notes: {
    items: Note[];
    current: Note | null;
    isLoading: boolean;
    error: Error | null;
  };
  ai: {
    tasks: Record<string, AITask>;
    results: Record<string, AIResult>;
  };
  collaboration: {
    activeUsers: User[];
    syncStatus: SyncStatus;
  };
  search: {
    results: SearchResult[];
    filters: SearchFilters;
    isLoading: boolean;
  };
}
```

### WebSocket Events
```typescript
// Collaboration Events
interface CollaborationEvents {
  'user:joined': (user: User) => void;
  'user:left': (user: User) => void;
  'change:applied': (change: Change) => void;
  'conflict:detected': (conflict: Conflict) => void;
}

// Sync Events
interface SyncEvents {
  'sync:started': () => void;
  'sync:completed': () => void;
  'sync:failed': (error: Error) => void;
}
```

## 3. API Response Formats

### Note Object
```typescript
interface Note {
  id: string;
  title: string;
  content: string;
  tags: string[];
  created_at: string;
  updated_at: string;
  version: string;
  collaborators: User[];
  attachments: Attachment[];
}
```

### AI Response
```typescript
interface AIResponse {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  result?: {
    summary?: string;
    explanation?: string;
    suggestions?: string[];
    questions?: StudyQuestion[];
  };
  error?: string;
}
```

### Version Control
```typescript
interface Version {
  id: string;
  commit_hash: string;
  message: string;
  timestamp: string;
  author: User;
  changes: Change[];
}
```

## 4. Error Handling

### Backend Error Responses
```typescript
interface APIError {
  status: number;
  code: string;
  message: string;
  details?: Record<string, any>;
}
```

Frontend should handle these common error scenarios:
1. Authentication failures (401)
2. Permission denied (403)
3. Resource not found (404)
4. Validation errors (422)
5. Server errors (500)
6. Network connectivity issues
7. WebSocket connection failures

## 5. Security Considerations

### CORS Configuration
Backend has CORS configured for:
- Frontend development server
- Production domain
- WebSocket connections

### Authentication
- JWT tokens with refresh mechanism
- Token storage in HttpOnly cookies
- CSRF protection
- Rate limiting on sensitive endpoints

## 6. Performance Optimization

### Backend Optimizations
- Redis caching for frequently accessed data
- Background task processing for heavy operations
- WebSocket connection pooling
- Database query optimization

### Frontend Requirements
- Implement client-side caching
- Use WebSocket connection management
- Implement progressive loading
- Optimize bundle size
- Use service workers for offline support

## 7. Development Setup

### Required Environment Variables
Frontend (.env):
```env
REACT_APP_API_URL=http://localhost:5000
REACT_APP_WS_URL=ws://localhost:5000
REACT_APP_ENV=development
```

Backend (.env):
```env
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000
WS_ALLOWED_ORIGINS=http://localhost:3000
```

## 8. Testing Requirements

### Backend Tests
- Unit tests for services
- Integration tests for API endpoints
- WebSocket connection tests
- Task processing tests

### Frontend Tests
- Component rendering tests
- State management tests
- API integration tests
- WebSocket communication tests
- Error handling tests

## 9. Deployment Considerations

### Backend Services
- API server (Flask/Gunicorn)
- WebSocket server
- Celery workers
- Redis
- MongoDB
- Elasticsearch

### Frontend Build
- Static file hosting
- Environment configuration
- CDN setup
- Cache management

## 10. Monitoring and Logging

### Backend Metrics
- Request/response times
- WebSocket connection stats
- Task processing times
- Error rates
- Resource usage

### Frontend Monitoring
- Page load times
- API call performance
- WebSocket connection stability
- Error tracking
- User interactions

This alignment guide ensures that both frontend and backend teams understand the integration points and requirements for successful development and deployment.
