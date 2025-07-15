# 🚀 Backend API - AI Voice Cloning Platform

> **FastAPI backend service with secure authentication, token management, and AI-powered video generation.**

## 🌟 Overview

The backend powers the AI Voice Cloning Platform with REST API endpoints for user management, character creation, script generation, and video production. Built with FastAPI, Firebase, and integrated AI services.

### ✨ Core Features

- **🔐 JWT Authentication** with Firebase Auth integration
- **🪙 Token System** with configurable credits and billing
- **👥 Character Management** with voice cloning capabilities
- **📝 AI Script Generation** using OpenAI GPT models
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

## 🚀 Quick Setup

### Install Dependencies
```bash
python -m venv env
source env/bin/activate  # or env\Scripts\activate on Windows
pip install -r requirements.txt
```

### Environment Configuration
```bash
# Create .env file
OPENAI_API_KEY=your_openai_key_here
TOKENS_TO_GIVE=20
JWT_SECRET=your_jwt_secret_here
```

### Firebase Setup
Place your Firebase service account credentials in `firebase.json`:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "...",
  "client_email": "...",
  "client_id": "..."
}
```

### Start Development Server
```bash
python app.py
# Server runs on http://localhost:8000
```

## 📋 Key API Endpoints

### Authentication
- `POST /api/signup` - User registration
- `POST /api/login` - User authentication  
- `GET /api/me` - Current user profile
- `POST /api/refresh-token` - Token renewal

### Characters
- `GET /api/characters` - List all characters
- `POST /api/characters/complete` - Create new character
- `PUT /api/characters/{id}` - Update character
- `DELETE /api/characters/{id}` - Delete character

### Scripts & Videos
- `POST /api/scripts/generate` - Generate new script
- `GET /api/my-scripts` - User's scripts with token info
- `POST /api/scripts/{id}/generate-video` - Start video generation
- `GET /api/scripts/{id}/video-status` - Check video progress

### User Management
- `GET /api/my-activities` - User activity log
- `GET /api/my-favorites` - Favorite characters
- `POST /api/characters/{id}/star` - Star/unstar character

## 🪙 Token System

- **Initial Balance**: Users receive configurable tokens on signup (default: 20)
- **Video Generation Cost**: 1 token per video
- **Pre-validation**: Token balance checked before generation starts
- **Post-deduction**: Tokens deducted only on successful completion
- **Activity Logging**: All token transactions logged

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Input Validation**: Pydantic models for all requests
- **File Upload Security**: Type and size restrictions
- **Ownership Checks**: Users can only modify their own content
- **Error Handling**: Secure error responses

## 🚀 Production Deployment

```bash
# Install production dependencies
pip install -r requirements.txt

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

## 🔧 Development

### Local Development
```bash
# Start development server with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000
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

## 🐛 Troubleshooting

**Firebase Connection Error:**
```bash
# Check Firebase credentials
cat firebase.json
```

**F5-TTS Service Unavailable:**
```bash
# Check service status
curl http://localhost:7860/
```

**JWT Token Issues:**
```bash
# Check JWT secret configuration
echo $JWT_SECRET
```

---

**🚀 Ready to Power Amazing AI Videos! ✨**
