# TrackerWorkflow API

A FastAPI-based backend for the Workflow Tracker application with support for both traditional email/password authentication and Google OAuth.

## Features

- **User Authentication**: Traditional email/password login and registration
- **Google OAuth**: Single Sign-On with Google accounts
- **Project Management**: Full CRUD operations for projects
- **Task Management**: Full CRUD operations for tasks with status tracking
- **JWT Authentication**: Secure token-based authentication
- **Database**: SQLite database with SQLAlchemy ORM

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the root directory with the following variables:

```env
# Database Configuration
DATABASE_URL=sqlite:///./trackerworkflow.db

# JWT Configuration
SECRET_KEY=your-secret-key-here-make-it-long-and-random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

### 3. Google OAuth Setup

To enable Google OAuth, you need to:

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create a new project** or select an existing one
3. **Enable Google+ API** and **Google OAuth2 API**
4. **Create OAuth 2.0 credentials**:
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:8000/auth/google/callback`
   - Copy the Client ID and Client Secret to your `.env` file

### 4. Frontend Configuration

Update the Google Client ID in `TrackerWorkflow/src/components/GoogleLogin.jsx`:

```javascript
client_id: 'your-actual-google-client-id', // Replace with your actual client ID
```

### 5. Run the Application

```bash
# Start the backend
python main.py

# Or with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## API Endpoints

### Authentication

- `POST /register` - User registration
- `POST /login` - Traditional login
- `POST /auth/google` - Google OAuth login
- `GET /auth/google/url` - Get Google OAuth URL
- `GET /me` - Get current user info

### Projects

- `POST /projects` - Create project
- `GET /projects` - Get all projects
- `GET /projects/{project_id}` - Get specific project
- `PUT /projects/{project_id}` - Update project
- `DELETE /projects/{project_id}` - Delete project

### Tasks

- `POST /tasks` - Create task
- `GET /tasks` - Get all tasks
- `GET /tasks/project/{project_id}` - Get tasks by project
- `GET /tasks/{task_id}` - Get specific task
- `PUT /tasks/{task_id}` - Update task
- `DELETE /tasks/{task_id}` - Delete task

## Database Schema

### Users Table

- `id` - Primary key
- `email` - User email (unique)
- `password` - Hashed password (nullable for Google users)
- `name` - User display name
- `avatar_url` - Profile picture URL
- `google_id` - Google OAuth ID (unique, nullable)
- `auth_provider` - Authentication method ("email" or "google")
- `is_active` - Account status
- `created_at` - Account creation timestamp
- `updated_at` - Last update timestamp

### Projects Table

- `id` - Primary key
- `name` - Project name
- `description` - Project description
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

### Tasks Table

- `id` - Primary key
- `title` - Task title
- `description` - Task description
- `status` - Task status (TODO, IN_PROGRESS, REVIEW, DONE)
- `priority` - Task priority (LOW, MEDIUM, HIGH)
- `assignee` - Task assignee
- `due_date` - Task due date
- `project_id` - Foreign key to projects table
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

## Task Status and Priority Values

### Task Status

- `TODO` - Task not started
- `IN_PROGRESS` - Task in progress
- `REVIEW` - Task under review
- `DONE` - Task completed

### Task Priority

- `LOW` - Low priority
- `MEDIUM` - Medium priority (default)
- `HIGH` - High priority

## Testing

### Test Project API

```bash
python test_api.py
```

### Test Task API

```bash
python test_task_api.py
```

## Security Features

- **Password Hashing**: Bcrypt password hashing for traditional users
- **JWT Tokens**: Secure authentication tokens
- **Google OAuth**: Verified Google account authentication
- **Input Validation**: Pydantic schema validation
- **SQL Injection Protection**: SQLAlchemy ORM protection

## Development Notes

- The application uses SQLite for development (easier setup)
- Google OAuth users don't need passwords
- Users can switch between authentication methods
- All API endpoints require authentication except login/register
- CORS is enabled for local development

<!-- Run Backend -->

venv\Scripts\activate
