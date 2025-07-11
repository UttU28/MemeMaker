# 🚀 Backend API - AI Voice Cloning Platform

> **FastAPI-powered backend service providing secure authentication, token management, and AI-driven video generation capabilities.**

## 🌟 Overview

This FastAPI backend serves as the core engine for the AI Voice Cloning Platform, providing:

- **🔐 JWT Authentication** with Firebase Auth integration
- **🪙 Token-based Billing System** with configurable credits
- **👥 Character Management** with voice cloning capabilities
- **📝 Script Generation** using OpenAI GPT models
- **🎬 Background Video Processing** with progress tracking
- **📊 User Activity Tracking** and analytics
- **⭐ Social Features** for community engagement

## 🛠️ Technology Stack

- **FastAPI** - High-performance Python web framework
- **Firebase Firestore** - NoSQL database for data storage
- **Firebase Auth** - User authentication and management
- **JWT Tokens** - Secure authentication tokens
- **Pydantic** - Data validation and serialization
- **F5-TTS** - Advanced voice cloning technology
- **OpenAI GPT** - AI script generation
- **FFmpeg** - Video processing and encoding
- **Uvicorn** - ASGI server for production deployment

## 📁 Project Structure

```
backend/
├── 🚀 app.py                          # Main FastAPI application
├── 📊 models.py                       # Pydantic data models
├── 🔥 firebase_service.py             # Firebase integration
├── 🔐 jwt_service.py                  # JWT token management
├── 🎤 audio_service.py                # F5-TTS integration
├── 🎬 video_service.py                # Video generation
├── 🔄 background_video_service.py     # Background processing
├── 🛠️ utils.py                        # Utility functions
├── 📦 requirements.txt                # Dependencies
├── 🔧 .env                            # Environment variables
└── 🔑 firebase.json                   # Firebase credentials
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Firebase Project with Firestore enabled
- OpenAI API key
- F5-TTS service running on port 7860

### 1. Virtual Environment
```bash
python -m venv env
# Windows
env\Scripts\activate
# Linux/Mac
source env/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
# Create .env file
OPENAI_API_KEY=your_openai_key_here
TOKENS_TO_GIVE=20
JWT_SECRET=your_jwt_secret_here
```

### 4. Firebase Setup
Place your Firebase service account credentials in `firebase.json`:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "...",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}
```

### 5. Start Development Server
```bash
python app.py
# Server runs on http://localhost:8000
```

## 📋 API Documentation

### Base URL
```
Development: http://localhost:8000
Production: https://your-domain.com
```

### Authentication
All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

## 🔐 Authentication Endpoints

### POST /api/signup
Create a new user account.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User created successfully",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user_123",
    "name": "John Doe",
    "email": "john@example.com",
    "tokens": 20,
    "isVerified": false,
    "subscription": "free",
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-01T00:00:00Z"
  },
  "expiresIn": 3600
}
```

### POST /api/login
Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user_123",
    "name": "John Doe",
    "email": "john@example.com",
    "tokens": 15,
    "isVerified": false,
    "subscription": "free",
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-01T00:00:00Z"
  },
  "expiresIn": 3600
}
```

### GET /api/me
Get current user profile (requires authentication).

**Response:**
```json
{
  "id": "user_123",
  "name": "John Doe",
  "email": "john@example.com",
  "tokens": 15,
  "isVerified": false,
  "subscription": "free",
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

### POST /api/refresh-token
Refresh JWT token before expiration.

**Response:**
```json
{
  "success": true,
  "message": "Token refreshed successfully",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": { ... },
  "expiresIn": 3600
}
```

## 👥 Character Management Endpoints

### GET /api/characters
List all public characters.

**Response:**
```json
[
  {
    "id": "character_123",
    "displayName": "Modi",
    "audioFile": "/api/static/audio_files/Modi.wav",
    "config": {
      "speed": 1.0,
      "nfeSteps": 32,
      "crossFadeDuration": 0.15,
      "removeSilences": true
    },
    "images": {
      "0": "/api/static/images/modi_confident.png",
      "1": "/api/static/images/modi_serious.png"
    },
    "outputPrefix": "modi",
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-01T00:00:00Z",
    "hasAudio": true,
    "imageCount": 2,
    "createdBy": "user_456",
    "createdByName": "Admin User",
    "isOwner": false,
    "starred": 25,
    "isStarred": false
  }
]
```

### GET /api/my-characters
Get characters created by current user.

**Response:**
```json
[
  {
    "id": "character_789",
    "displayName": "My Character",
    "audioFile": "/api/static/audio_files/my_character.wav",
    "config": { ... },
    "images": { ... },
    "outputPrefix": "my_character",
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-01T00:00:00Z",
    "hasAudio": true,
    "imageCount": 3,
    "createdBy": "user_123",
    "createdByName": "John Doe",
    "isOwner": true,
    "starred": 5,
    "isStarred": false
  }
]
```

### POST /api/characters/complete
Create a new character with audio and images.

**Request (multipart/form-data):**
```
displayName: "My New Character"
speed: 1.2
nfeSteps: 28
crossFadeDuration: 0.2
removeSilences: true
audioFile: [audio file]
imageFiles: [image files array]
```

**Response:**
```json
{
  "id": "character_new",
  "displayName": "My New Character",
  "audioFile": "/api/static/audio_files/character_new.wav",
  "config": {
    "speed": 1.2,
    "nfeSteps": 28,
    "crossFadeDuration": 0.2,
    "removeSilences": true
  },
  "images": {
    "0": "/api/static/images/character_new_0.png",
    "1": "/api/static/images/character_new_1.png"
  },
  "outputPrefix": "character_new",
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z",
  "hasAudio": true,
  "imageCount": 2,
  "createdBy": "user_123",
  "createdByName": "John Doe",
  "isOwner": true,
  "starred": 0,
  "isStarred": false
}
```

### PUT /api/characters/{character_id}
Update an existing character (owner only).

**Request (multipart/form-data):**
```
displayName: "Updated Character Name"
speed: 1.1
newImageFiles: [new image files]
removeImageKeys: "0,2"
```

### DELETE /api/characters/{character_id}
Delete a character (owner only).

**Response:**
```json
{
  "message": "Character 'character_123' deleted successfully",
  "deletedFiles": [
    "data/audio_files/character_123.wav",
    "data/images/character_123_0.png"
  ]
}
```

### POST /api/characters/{character_id}/star
Star a character.

**Response:**
```json
{
  "success": true,
  "message": "Character starred successfully",
  "characterId": "character_123",
  "starred": 26,
  "isStarred": true
}
```

### DELETE /api/characters/{character_id}/star
Unstar a character.

**Response:**
```json
{
  "success": true,
  "message": "Character unstarred successfully",
  "characterId": "character_123",
  "starred": 25,
  "isStarred": false
}
```

## 📝 Script Management Endpoints

### POST /api/scripts/generate
Generate a new script using AI.

**Request Body:**
```json
{
  "selectedCharacters": ["character_123", "character_456"],
  "prompt": "Create a conversation about climate change between two political leaders discussing renewable energy solutions."
}
```

**Response:**
```json
{
  "id": "script_789",
  "selectedCharacters": ["character_123", "character_456"],
  "originalPrompt": "Create a conversation about climate change...",
  "dialogue": [
    {
      "speaker": "character_123",
      "text": "Climate change is one of the most pressing issues of our time.",
      "audioFile": ""
    },
    {
      "speaker": "character_456",
      "text": "Absolutely, we need to invest heavily in renewable energy.",
      "audioFile": ""
    }
  ],
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z",
  "hasAudio": false,
  "audioCount": 0,
  "finalVideoPath": null,
  "videoDuration": null
}
```

### GET /api/my-scripts
Get user's scripts with token information.

**Response:**
```json
{
  "scripts": [
    {
      "id": "script_789",
      "selectedCharacters": ["character_123", "character_456"],
      "originalPrompt": "Create a conversation about climate change...",
      "dialogue": [ ... ],
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-01T00:00:00Z",
      "hasAudio": true,
      "audioCount": 8,
      "finalVideoPath": "/api/videos/script_789_final.mp4",
      "videoDuration": 45.2,
      "videoSize": 8543210,
      "videoJobId": "job_123",
      "videoJobStatus": "completed",
      "videoJobProgress": 100.0,
      "videoJobCurrentStep": "completed",
      "videoJobStartedAt": "2024-01-01T00:05:00Z",
      "videoJobCompletedAt": "2024-01-01T00:08:00Z",
      "videoJobErrorMessage": null
    }
  ],
  "userTokens": 15
}
```

### PUT /api/scripts/{script_id}
Update script dialogue.

**Request Body:**
```json
{
  "dialogue": [
    {
      "speaker": "character_123",
      "text": "Updated dialogue text here.",
      "audioFile": ""
    }
  ]
}
```

### DELETE /api/scripts/{script_id}
Delete a script (owner only).

**Response:**
```json
{
  "message": "Script 'script_123' deleted successfully",
  "deletedMediaFiles": [
    "data/audio_files/script_123_line_0.wav",
    "data/video_output/script_123_final.mp4"
  ],
  "deletedCount": 2
}
```

## 🎬 Video Generation Endpoints

### POST /api/scripts/{script_id}/generate-video
Start video generation for a script.

**Request Body:**
```json
{
  "backgroundVideo": "background_005.mp4"
}
```

**Response:**
```json
{
  "job": {
    "jobId": "job_456",
    "scriptId": "script_123",
    "userId": "user_123",
    "status": "queued",
    "overallProgress": 0.0,
    "currentStep": "",
    "steps": [
      {
        "stepName": "audio_validation",
        "status": "pending",
        "progress": 0.0,
        "message": "",
        "startedAt": null,
        "completedAt": null,
        "errorMessage": null
      }
    ],
    "totalSteps": 5,
    "completedSteps": 0,
    "createdAt": "2024-01-01T00:00:00Z",
    "startedAt": null,
    "completedAt": null,
    "finalVideoPath": null,
    "videoDuration": null,
    "videoSize": null,
    "errorMessage": null
  },
  "message": "Video generation started successfully! Job ID: job_456"
}
```

### GET /api/scripts/{script_id}/video-status
Check video generation status.

**Response:**
```json
{
  "scriptId": "script_123",
  "status": "in_progress",
  "stage": "audio_generation",
  "progress": 45.0,
  "message": "Generating audio files... (3/8 completed)",
  "startedAt": "2024-01-01T00:00:00Z",
  "completedAt": null,
  "errorMessage": null,
  "finalVideoPath": null
}
```

### GET /api/video-jobs/{job_id}
Get detailed video generation job information.

**Response:**
```json
{
  "jobId": "job_456",
  "scriptId": "script_123",
  "userId": "user_123",
  "status": "in_progress",
  "overallProgress": 67.5,
  "currentStep": "video_generation",
  "steps": [
    {
      "stepName": "audio_validation",
      "status": "completed",
      "progress": 100.0,
      "message": "Found 8/8 audio files",
      "startedAt": "2024-01-01T00:00:00Z",
      "completedAt": "2024-01-01T00:00:30Z",
      "errorMessage": null
    },
    {
      "stepName": "video_generation",
      "status": "in_progress",
      "progress": 35.0,
      "message": "Rendering video segments...",
      "startedAt": "2024-01-01T00:02:00Z",
      "completedAt": null,
      "errorMessage": null
    }
  ],
  "totalSteps": 5,
  "completedSteps": 2,
  "createdAt": "2024-01-01T00:00:00Z",
  "startedAt": "2024-01-01T00:00:00Z",
  "completedAt": null,
  "finalVideoPath": null,
  "videoDuration": null,
  "videoSize": null,
  "errorMessage": null
}
```

## 📊 User Activity Endpoints

### GET /api/my-activities
Get user's activity log.

**Query Parameters:**
- `limit`: Number of activities to return (default: 50)

**Response:**
```json
{
  "activities": [
    {
      "id": "activity_123",
      "type": "video_generation_completed",
      "message": "Video generation completed successfully for script 'Climate Change Discussion'",
      "timestamp": "2024-01-01T00:08:00Z",
      "scriptId": "script_123",
      "characterId": null,
      "videoPath": "/api/videos/script_123_final.mp4"
    }
  ],
  "totalCount": 1,
  "limit": 50
}
```

### GET /api/my-activity-stats
Get user's activity statistics.

**Response:**
```json
{
  "scriptActivities": 5,
  "characterActivities": 3,
  "videoActivities": 2,
  "totalActivities": 10,
  "lastActivityAt": "2024-01-01T00:08:00Z"
}
```

### DELETE /api/my-activities
Clear all user activities.

**Response:**
```json
{
  "message": "All activities cleared successfully",
  "success": true
}
```

## 🪙 Token System

### Token Management
- **Initial Balance**: Users receive configurable tokens on signup (default: 20)
- **Video Generation Cost**: 1 token per video
- **Pre-validation**: Token balance checked before generation starts
- **Post-deduction**: Tokens deducted only on successful completion
- **Activity Logging**: All token transactions logged

### Token Validation Flow
1. User requests video generation
2. System checks `user.tokens >= 1`
3. If insufficient, returns HTTP 400 error
4. If sufficient, video generation starts
5. On completion, 1 token deducted
6. Success/failure logged in user activities

## 🔒 Security Features

### Authentication
- **JWT Tokens**: Secure authentication with expiration
- **Firebase Integration**: Industry-standard user management
- **Password Security**: Firebase handles password hashing
- **Token Refresh**: Automatic token renewal

### Data Protection
- **Input Validation**: Pydantic models for all requests
- **File Upload Security**: Type and size restrictions
- **Ownership Checks**: Users can only modify their own content
- **Rate Limiting**: Token-based usage control

### Error Handling
- **Secure Error Messages**: No sensitive data exposed
- **Comprehensive Logging**: All operations logged
- **Exception Handling**: Graceful error recovery
- **Validation Errors**: Clear user feedback

## 🚀 Deployment

### Production Environment
```bash
# Install production dependencies
pip install -r requirements.txt

# Set production environment variables
export ENVIRONMENT=production
export JWT_SECRET=your_production_secret
export TOKENS_TO_GIVE=20

# Start with Uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_openai_api_key
JWT_SECRET=your_jwt_secret

# Optional
TOKENS_TO_GIVE=20
ENVIRONMENT=development
DATABASE_URL=your_database_url
```

## 📈 Performance Optimization

### Async Operations
- **Background Processing**: Non-blocking video generation
- **Efficient Database Queries**: Optimized Firebase operations
- **Concurrent Requests**: FastAPI async support
- **Connection Pooling**: Database connection optimization

### Caching Strategy
- **User Sessions**: JWT token caching
- **Static Files**: Efficient file serving
- **Database Queries**: Query result caching
- **API Responses**: Response caching for public data

## 🐛 Troubleshooting

### Common Issues

**Firebase Connection Error:**
```bash
# Check Firebase credentials
cat firebase.json
# Verify project permissions
```

**F5-TTS Service Unavailable:**
```bash
# Check service status
curl http://localhost:7860/
# Restart F5-TTS service
cd F5-TTS && python -m f5_tts.gradio_app
```

**JWT Token Issues:**
```bash
# Check JWT secret configuration
echo $JWT_SECRET
# Verify token expiration settings
```

**Video Generation Failures:**
```bash
# Check CUDA availability
nvidia-smi
# Verify FFmpeg installation
ffmpeg -version
```

## 📊 Monitoring & Logging

### Application Logs
- **Request/Response Logging**: All API interactions
- **Error Tracking**: Comprehensive error logging
- **Performance Metrics**: Response time monitoring
- **User Activity**: Detailed activity logging

### Health Checks
- **Database Health**: Firebase connection status
- **Service Health**: F5-TTS service availability
- **System Resources**: CPU, memory, disk usage
- **API Status**: Endpoint availability

## 🔧 Development

### Local Development
```bash
# Start development server with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/

# Code formatting
black app.py
flake8 app.py
```

### API Testing
```bash
# Test authentication
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass"}'

# Test protected endpoint
curl -X GET http://localhost:8000/api/me \
  -H "Authorization: Bearer your_jwt_token"
```

## 📚 Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Firebase Documentation**: https://firebase.google.com/docs
- **F5-TTS Repository**: https://github.com/SWivid/F5-TTS
- **OpenAI API**: https://platform.openai.com/docs

---

**🚀 Ready to Power Amazing AI Videos! ✨**
