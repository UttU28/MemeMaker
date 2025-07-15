# 🎬 AI Voice Cloning & Video Generation Platform

> **Transform text prompts into professional videos with AI-generated scripts, cloned voices, and dynamic visuals.**

## 🌟 Overview

A full-stack platform that combines cutting-edge AI technologies to create a complete video production pipeline. Users can generate custom scripts, clone voices, and produce professional-quality videos with secure authentication and token-based billing.

### ✨ Key Features

- **🔐 User Authentication** - JWT-based auth with Firebase
- **🪙 Token-Based Billing** - Credit system for video generation
- **🤖 AI Script Generation** - Natural dialogue using OpenAI GPT
- **🎤 Voice Cloning** - High-quality speech synthesis with F5-TTS
- **👥 Character Management** - Create voice characters with emotions
- **🎥 Automated Video Production** - Background processing with progress tracking
- **📱 Modern Web Interface** - Responsive React app with Material-UI
- **⭐ Social Features** - Star characters and track activities

## 🛠️ Technology Stack

**Frontend:** React 18 + TypeScript + Material-UI + Vite  
**Backend:** FastAPI + Python + Firebase + JWT  
**AI Services:** OpenAI GPT + F5-TTS + FFmpeg  
**Database:** Firebase Firestore + Firebase Auth  

## 📁 Project Structure

```
VoiceClonning_F5-TTS/
├── 🖥️ frontend/          # React TypeScript app
├── 🖧 backend/           # FastAPI Python server
├── 📊 data/              # Media assets and data
└── 🏗️ F5-TTS/           # Voice cloning engine
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and Python 3.8+
- Firebase project with Firestore
- OpenAI API key
- NVIDIA GPU (recommended)

### Setup
```bash
# Backend
cd backend
pip install -r requirements.txt
python app.py  # Runs on :8000

# Frontend
cd frontend
npm install
npm run dev    # Runs on :5173

# F5-TTS Service
cd F5-TTS
pip install -e .
python -m f5_tts.gradio_app  # Runs on :7860
```

### Configuration
```bash
# backend/.env
OPENAI_API_KEY=your_key_here
TOKENS_TO_GIVE=20
JWT_SECRET=your_secret

# backend/firebase.json
{Firebase service account credentials}
```

## 🎯 How It Works

1. **Register & Login** - Create account, receive tokens
2. **Create Characters** - Upload voice samples and images
3. **Generate Scripts** - AI creates dialogue between characters
4. **Produce Videos** - Automated video generation with progress tracking
5. **Manage Content** - View videos, track usage, favorite characters

## 🔧 Development

**Start All Services:**
```bash
# Terminal 1: Backend
cd backend && python app.py

# Terminal 2: Frontend  
cd frontend && npm run dev

# Terminal 3: F5-TTS
cd F5-TTS && python -m f5_tts.gradio_app
```

**Production Build:**
```bash
cd frontend && npm run build
cd backend && uvicorn app:app --host 0.0.0.0 --port 8000
```

## 📚 Documentation

- **Backend API:** See `backend/README.md`
- **Frontend App:** See `frontend/README.md`
- **Detailed Setup:** Check individual service documentation

---

**🎬 Create Amazing Videos with AI! ✨** 