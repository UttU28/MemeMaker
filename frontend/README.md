# ⚛️ Frontend - AI Voice Cloning Platform

> **Modern React TypeScript application with Material-UI for AI-powered video generation.**

## 🌟 Overview

The React frontend provides an intuitive interface for the AI Voice Cloning Platform with responsive design, real-time updates, and seamless user experience. Built with React 18, TypeScript, and Material-UI.

### ✨ Key Features

- **🔐 Secure Authentication** with JWT token management
- **📱 Responsive Design** with Material-UI components
- **🎨 Modern UI/UX** with glassmorphism effects
- **⚡ Real-time Updates** with efficient polling
- **🎬 Video Generation** with progress tracking
- **👥 Character Management** with creation and editing
- **📝 Script Editor** with AI-powered generation
- **🪙 Token System** with live balance updates
- **⭐ Social Features** for community engagement

## 🛠️ Technology Stack

- **React 18** - Modern React with hooks and concurrent features
- **TypeScript** - Type-safe JavaScript for better development
- **Material-UI (MUI)** - Comprehensive React component library
- **Vite** - Fast build tool and development server
- **React Router** - Client-side routing and navigation
- **Axios** - HTTP client for API communication
- **Context API** - State management for authentication

## 📁 Project Structure

```
frontend/
├── 📁 src/
│   ├── 🎨 components/         # Reusable UI components
│   │   ├── 🎯 tabs/          # Tab-based page components
│   │   ├── Dashboard.tsx
│   │   ├── DashboardLayout.tsx
│   │   └── Sidebar.tsx
│   ├── 📄 pages/             # Application pages
│   ├── 🎯 contexts/          # React contexts
│   ├── 🔧 services/          # API integration
│   ├── App.tsx               # Main application component
│   ├── main.tsx              # Application entry point
│   └── theme.ts              # Material-UI theme
├── 📦 package.json
└── ⚙️ vite.config.ts
```

## 🚀 Quick Setup

### Install Dependencies
```bash
npm install
```

### Start Development Server
```bash
npm run dev
# Application runs on http://localhost:5173
```

### Build for Production
```bash
npm run build
# Creates optimized build in dist/
```

### Preview Production Build
```bash
npm run preview
# Serves production build locally
```

## 🎯 Key Components

### Core Components
- **App.tsx** - Main application with routing and theme
- **AuthProvider.tsx** - Authentication context with JWT management
- **DashboardLayout.tsx** - Main layout with sidebar navigation

### Tab Components
- **CharactersTab.tsx** - Character management interface
- **ScriptsTab.tsx** - Script management with AI generation
- **VideosTab.tsx** - Video management and progress tracking
- **ProfileTab.tsx** - User profile and account settings

## 🔧 Configuration

### Environment Variables
```typescript
// vite-env.d.ts
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_APP_VERSION: string;
}
```

### API Integration
```typescript
// services/api.ts
const API_BASE_URL = 'http://localhost:8000';

// Axios instance with JWT token interceptor
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

## 🎨 Styling & Theme

### Material-UI Theme
```typescript
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#6366f1',
    },
    background: {
      default: '#0f172a',
      paper: 'rgba(30, 41, 59, 0.8)',
    },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(148, 163, 184, 0.1)',
        },
      },
    },
  },
});
```

## 🚀 Development

### Local Development
```bash
# Start development server
npm run dev

# Run with specific port
npm run dev -- --port 3000
```

### Production Build
```bash
npm run build
npm run preview
```

## 📱 Mobile Optimization

- **Responsive Grid System** with Material-UI breakpoints
- **Touch-friendly Interactions** for mobile devices
- **Optimized Performance** with code splitting and lazy loading
- **Progressive Web App** features

## 🔧 Performance Features

- **Code Splitting** with React.lazy()
- **Memoization** with React.memo and useMemo
- **Efficient Re-rendering** with useCallback
- **Bundle Optimization** with Vite

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage
```

## 🚀 Deployment

### Static Hosting
```bash
# Build for production
npm run build

# Deploy to Netlify
netlify deploy --dir=dist --prod

# Deploy to Vercel
vercel --prod
```

---

**⚛️ Build Amazing User Experiences! ✨**
