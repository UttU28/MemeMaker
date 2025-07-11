# �� AI Voice Cloning & Video Generation Platform

> **A comprehensive full-stack platform that transforms text prompts into professional videos with AI-generated scripts, cloned voices, and dynamic visuals - featuring user authentication, token-based billing, and real-time progress tracking.**

## 🌟 Project Overview

This sophisticated platform combines cutting-edge AI technologies to create a complete video production pipeline. Users can generate custom scripts, clone voices, and produce professional-quality videos with an intuitive web interface, secure authentication, and a token-based billing system.

### ✨ Key Features

- **🔐 User Authentication**: Secure JWT-based authentication with Firebase integration
- **🪙 Token-Based Billing**: Credit system for video generation (configurable token amounts)
- **🤖 AI Script Generation**: Natural dialogue creation using OpenAI GPT models
- **🎤 Voice Cloning**: High-quality speech synthesis with F5-TTS
- **👥 Character Management**: Create and manage voice characters with emotional expressions
- **🎥 Automated Video Production**: Background processing with real-time progress tracking
- **📱 Modern Web Interface**: Responsive React app with Material-UI components
- **⭐ Social Features**: Star favorite characters and track user activities
- **🔄 Real-Time Updates**: Live progress tracking and token balance updates

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + TypeScript)               │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│ │  Authentication │ │   Dashboard     │ │   Video Gen     │   │
│ │   & Profile     │ │  & Characters   │ │  & Scripts      │   │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ REST API + JWT
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI + Python)                  │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│ │  Authentication │ │   Token System  │ │ Background Jobs │   │
│ │   & User Mgmt   │ │  & Validation   │ │ & Video Gen     │   │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ Firebase SDK
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE (Firebase Firestore)               │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│ │      Users      │ │   Characters    │ │    Scripts      │   │
│ │   & Tokens      │ │  & Favorites    │ │  & Video Jobs   │   │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 🛠️ Technology Stack

### Frontend
- **⚛️ React 18** with TypeScript
- **🎨 Material-UI (MUI)** for modern UI components
- **🔄 React Router** for navigation
- **🏗️ Vite** for fast development and building
- **📱 Responsive Design** with glassmorphism effects

### Backend
- **🚀 FastAPI** with Python 3.8+
- **🔐 JWT Authentication** with Firebase Auth
- **📊 Pydantic** for data validation
- **🎤 F5-TTS** for voice cloning
- **🤖 OpenAI GPT** for script generation
- **🎬 FFmpeg** for video processing

### Database & Infrastructure
- **🔥 Firebase Firestore** for data storage
- **🔑 Firebase Auth** for user management
- **⚡ Background Processing** with async tasks
- **📈 Real-time Updates** with polling

## 📁 Project Structure

```
VoiceClonning_F5-TTS/
├── 🖥️ frontend/                  # React TypeScript application
│   ├── 📁 src/
│   │   ├── 🎨 components/       # Reusable UI components
│   │   ├── 📄 pages/            # Application pages
│   │   ├── 🔧 services/         # API integration
│   │   ├── 🎯 contexts/         # React contexts
│   │   └── 🎨 theme.ts          # Material-UI theme
│   ├── 📦 package.json
│   └── ⚙️ vite.config.ts
│
├── 🖧 backend/                   # FastAPI Python application
│   ├── 🚀 app.py                # Main FastAPI application
│   ├── 📊 models.py             # Pydantic data models
│   ├── 🔥 firebase_service.py   # Firebase integration
│   ├── 🎤 audio_service.py      # F5-TTS integration
│   ├── 🎬 video_service.py      # Video generation
│   ├── 🔄 background_video_service.py  # Background processing
│   ├── 🔐 jwt_service.py        # JWT token management
│   └── 📦 requirements.txt
│
├── 📊 data/                      # Media assets and data
│   ├── 🎞️ background/           # Background videos
│   ├── 🖼️ images/               # Character expression images
│   ├── 🔊 audio_files/          # Voice samples
│   └── 🎥 video_output/         # Generated videos
│
├── 🏗️ F5-TTS/                   # Voice cloning engine
├── 🚀 main.py                   # Legacy CLI interface
└── 📚 README.md                 # This documentation
```

## 🚀 Installation & Setup

### Prerequisites
- **Node.js 18+** and npm
- **Python 3.8+** with pip
- **NVIDIA GPU** with CUDA support (recommended)
- **FFmpeg** with CUDA encoding
- **Firebase Project** with Firestore enabled

### 1. Clone Repository
```bash
git clone <repository-url>
cd VoiceClonning_F5-TTS
```

### 2. Backend Setup
```bash
cd backend
python -m venv env
# Windows
env\Scripts\activate
# Linux/Mac
source env/bin/activate

pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Firebase Configuration
```bash
# Place your Firebase credentials in backend/firebase.json
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

### 5. Environment Variables
```bash
# Create backend/.env
OPENAI_API_KEY=your_openai_key_here
TOKENS_TO_GIVE=20
JWT_SECRET=your_jwt_secret_here
```

### 6. Setup F5-TTS Service
```bash
cd F5-TTS
pip install -e .
# Start Gradio service
python -m f5_tts.gradio_app
```

## 🎯 Usage Guide

### Development Mode

**Start Backend Server:**
```bash
cd backend
python app.py
# Server runs on http://localhost:8000
```

**Start Frontend Development:**
```bash
cd frontend
npm run dev
# App runs on http://localhost:5173
```

**Start F5-TTS Service:**
```bash
cd F5-TTS
python -m f5_tts.gradio_app
# Service runs on http://localhost:7860
```

### Production Deployment

**Build Frontend:**
```bash
cd frontend
npm run build
# Creates optimized build in dist/
```

**Start Production Backend:**
```bash
cd backend
uvicorn app:app --host 0.0.0.0 --port 8000
```

## 🔄 Complete User Flow

### 1. **User Registration & Authentication**
- User creates account with email/password
- JWT token issued for session management
- Initial token balance assigned (configurable)

### 2. **Character Management**
- Create voice characters with audio samples
- Upload character images for different emotions
- Set voice configuration (speed, quality, etc.)
- Star favorite characters from community

### 3. **Script Generation**
- Select 2-5 characters for dialogue
- Provide text prompt for conversation topic
- AI generates natural dialogue between characters
- Edit and refine script as needed

### 4. **Video Production**
- Token validation before generation starts
- Background processing with progress tracking
- Audio generation for each dialogue line
- Video assembly with character images and backgrounds
- Token deduction upon successful completion

### 5. **Content Management**
- View generated videos and scripts
- Track user activity and statistics
- Manage token balance and usage
- Share and favorite community content

## 🎨 Key Features Deep Dive

### Authentication System
- **JWT-based Security**: Secure token authentication
- **Firebase Integration**: User management and data storage
- **Protected Routes**: Role-based access control
- **Token Refresh**: Automatic session renewal

### Token Management
- **Pre-validation**: Check balance before video generation
- **Post-deduction**: Charge only on successful completion
- **Activity Logging**: Track all token transactions
- **Real-time Updates**: Live balance updates in UI

### Character System
- **Voice Cloning**: High-quality speech synthesis
- **Emotion Support**: Multiple expressions per character
- **Community Features**: Star and favorite system
- **Ownership Tracking**: User-created content management

### Video Generation
- **Background Processing**: Async job queue system
- **Progress Tracking**: Real-time status updates
- **Quality Control**: Professional video output
- **Error Handling**: Robust failure recovery

## 🔧 API Endpoints

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
- `POST /api/characters/{id}/star` - Star character

### Scripts & Videos
- `POST /api/scripts/generate` - Generate new script
- `GET /api/my-scripts` - User's scripts with token info
- `PUT /api/scripts/{id}` - Update script
- `POST /api/scripts/{id}/generate-video` - Start video generation
- `GET /api/scripts/{id}/video-status` - Check video progress

### User Management
- `GET /api/my-activities` - User activity log
- `GET /api/my-favorites` - Favorite characters
- `GET /api/my-video-jobs` - Video generation jobs

## 📊 Performance & Scaling

### Optimization Features
- **GPU Acceleration**: CUDA-based video processing
- **Async Processing**: Non-blocking background jobs
- **Efficient Polling**: Smart progress updates
- **Caching**: Reduced regeneration overhead

### Quality Settings
- **Video**: 1080x1920 (mobile-optimized)
- **Audio**: 24kHz AAC, high-quality voice synthesis
- **Processing**: ~2-3 minutes per video
- **Storage**: Firebase Firestore for scalability

## 🛡️ Security Features

- **JWT Authentication**: Secure token-based auth
- **Input Validation**: Pydantic model validation
- **File Upload Security**: Type and size restrictions
- **Rate Limiting**: Token-based usage control
- **Error Handling**: Secure error responses

## 🚀 Future Enhancements

### Planned Features
- **Payment Integration**: Stripe/PayPal for token purchases
- **Advanced Analytics**: Usage statistics and insights
- **Mobile App**: React Native companion app
- **API Monetization**: Developer API access
- **Multi-language**: International voice support

### Technical Improvements
- **Microservices**: Service decomposition
- **Container Deployment**: Docker orchestration
- **CDN Integration**: Global content delivery
- **Real-time Notifications**: WebSocket integration

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Follow installation instructions
3. Create feature branch: `git checkout -b feature/new-feature`
4. Test thoroughly (frontend + backend)
5. Submit PR with detailed description

### Code Standards
- **TypeScript**: Strict type checking
- **Python**: PEP 8 style guidelines
- **Testing**: Unit tests for critical functions
- **Documentation**: Clear inline comments

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **F5-TTS**: Advanced voice cloning technology
- **OpenAI**: GPT models for script generation
- **Firebase**: Backend infrastructure and auth
- **Material-UI**: Modern React components
- **FastAPI**: High-performance Python framework

---

## 📞 Support

For technical support or questions:
- Check the detailed README files in `frontend/` and `backend/` directories
- Review API documentation in backend code
- Test with development mode before production deployment

**🎬 Create Amazing Videos with AI! ✨** 