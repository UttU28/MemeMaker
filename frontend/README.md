# ⚛️ Frontend - AI Voice Cloning Platform

> **Modern React TypeScript application with Material-UI providing an intuitive interface for AI-powered video generation.**

## 🌟 Overview

This React frontend serves as the user interface for the AI Voice Cloning Platform, featuring:

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
- **CSS-in-JS** - Styled components with theme support

## 📁 Project Structure

```
frontend/
├── 📁 src/
│   ├── 🎨 components/           # Reusable UI components
│   │   ├── 🎯 tabs/            # Tab-based page components
│   │   │   ├── CharactersTab.tsx
│   │   │   ├── ProfileTab.tsx
│   │   │   ├── ScriptsTab.tsx
│   │   │   └── VideosTab.tsx
│   │   ├── ConfirmDialog.tsx
│   │   ├── Dashboard.tsx
│   │   ├── DashboardLayout.tsx
│   │   ├── LoadingScreen.tsx
│   │   └── Sidebar.tsx
│   ├── 📄 pages/               # Application pages
│   │   ├── Auth.tsx
│   │   ├── CharactersPage.tsx
│   │   ├── ProfilePage.tsx
│   │   ├── ScriptsPage.tsx
│   │   └── VideosPage.tsx
│   ├── 🎯 contexts/            # React contexts
│   │   ├── AuthContext.ts
│   │   └── AuthProvider.tsx
│   ├── 🔧 services/            # API integration
│   │   └── api.ts
│   ├── 🎨 assets/              # Static assets
│   │   └── react.svg
│   ├── App.tsx                 # Main application component
│   ├── main.tsx                # Application entry point
│   ├── index.css               # Global styles
│   └── theme.ts                # Material-UI theme
├── 📦 package.json             # Dependencies and scripts
├── 📋 tsconfig.json            # TypeScript configuration
├── ⚙️ vite.config.ts           # Vite configuration
└── 📚 README.md                # This documentation
```

## 🚀 Installation & Setup

### Prerequisites
- Node.js 18+ and npm
- Backend API running on port 8000
- Modern web browser

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Development Server
```bash
npm run dev
# Application runs on http://localhost:5173
```

### 3. Build for Production
```bash
npm run build
# Creates optimized build in dist/
```

### 4. Preview Production Build
```bash
npm run preview
# Serves production build locally
```

## 🎨 Key Features

### 🔐 Authentication System
- **JWT Token Management**: Secure authentication with automatic refresh
- **Protected Routes**: Route-level authentication guards
- **User Profile**: Comprehensive user information display
- **Session Persistence**: Automatic login state restoration

### 👥 Character Management
- **Character Creation**: Upload audio samples and character images
- **Voice Configuration**: Adjust speed, quality, and audio settings
- **Image Gallery**: Multiple character expressions and emotions
- **Community Features**: Star and favorite characters
- **Ownership System**: Users can only edit their own characters

### 📝 Script Generation
- **AI-Powered Creation**: Generate natural dialogues using OpenAI
- **Character Selection**: Choose 2-5 characters for conversations
- **Real-time Editing**: Edit scripts with live preview
- **Progress Tracking**: Monitor script completion status
- **Auto-save**: Automatic saving of script changes

### 🎬 Video Generation
- **Token Validation**: Pre-flight token balance checks
- **Background Processing**: Non-blocking video generation
- **Progress Tracking**: Real-time updates with detailed steps
- **Quality Control**: Professional video output settings
- **Download Management**: Easy access to generated videos

### 🪙 Token System
- **Live Balance**: Real-time token count updates
- **Usage Tracking**: Detailed token transaction history
- **Cost Transparency**: Clear token costs before generation
- **Activity Logging**: Comprehensive usage analytics

## 🎯 Component Architecture

### Core Components

#### `App.tsx`
Main application component with routing and theme provider.

```typescript
function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </ThemeProvider>
  );
}
```

#### `AuthProvider.tsx`
Authentication context provider with JWT token management.

```typescript
const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  
  // JWT token management logic
  // API integration
  // User state management
  
  return (
    <AuthContext.Provider value={authValue}>
      {children}
    </AuthContext.Provider>
  );
};
```

#### `DashboardLayout.tsx`
Main layout component with sidebar navigation and responsive design.

```typescript
const DashboardLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <Box sx={{ display: 'flex' }}>
      <Sidebar />
      <Box component="main" sx={{ flexGrow: 1 }}>
        {children}
      </Box>
    </Box>
  );
};
```

### Tab Components

#### `CharactersTab.tsx`
Character management interface with grid layout and filtering.

**Features:**
- Character grid with image previews
- Create new character wizard
- Edit existing characters
- Star/unstar functionality
- Advanced filtering and search

#### `ScriptsTab.tsx`
Script management with AI generation and editing capabilities.

**Features:**
- Script creation with AI assistance
- Real-time script editing
- Character selection interface
- Progress tracking
- Video generation controls

#### `VideosTab.tsx`
Video management and generation progress tracking.

**Features:**
- Video list with thumbnails
- Generation progress indicators
- Download functionality
- Quality metrics display
- Batch operations

#### `ProfileTab.tsx`
User profile management and account settings.

**Features:**
- User information display
- Token balance and usage
- Activity history
- Account settings
- YouTube channel integration

## 🔧 State Management

### Authentication Context
```typescript
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  updateUserTokens: (tokens: number) => void;
}
```

### Component State Patterns
```typescript
// Form state management
const [formData, setFormData] = useState<FormData>({
  field1: '',
  field2: ''
});

// Loading states
const [loading, setLoading] = useState(false);
const [error, setError] = useState<string | null>(null);

// UI state
const [showDialog, setShowDialog] = useState(false);
const [selectedItem, setSelectedItem] = useState<Item | null>(null);
```

## 🎨 Styling & Theming

### Theme Configuration
```typescript
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#6366f1',
    },
    secondary: {
      main: '#f59e0b',
    },
    background: {
      default: '#0f172a',
      paper: 'rgba(30, 41, 59, 0.8)',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
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

### Glassmorphism Effects
```typescript
const glassmorphismStyle = {
  background: 'rgba(30, 41, 59, 0.8)',
  backdropFilter: 'blur(20px)',
  border: '1px solid rgba(148, 163, 184, 0.1)',
  borderRadius: 3,
};
```

## 📡 API Integration

### API Service Structure
```typescript
class APIService {
  private baseURL = 'http://localhost:8000';
  private axiosInstance: AxiosInstance;

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor for auth tokens
    this.axiosInstance.interceptors.request.use((config) => {
      const token = localStorage.getItem('authToken');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor for error handling
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle token expiration
          this.handleTokenExpiration();
        }
        return Promise.reject(error);
      }
    );
  }
}
```

### API Endpoints Usage
```typescript
// Authentication
const login = async (credentials: LoginCredentials) => {
  const response = await api.post('/api/login', credentials);
  return response.data;
};

// Characters
const getCharacters = async () => {
  const response = await api.get('/api/characters');
  return response.data;
};

// Scripts
const generateScript = async (request: ScriptRequest) => {
  const response = await api.post('/api/scripts/generate', request);
  return response.data;
};

// Video Generation
const generateVideo = async (scriptId: string) => {
  const response = await api.post(`/api/scripts/${scriptId}/generate-video`);
  return response.data;
};
```

## 🔄 Real-time Updates

### Polling Strategy
```typescript
const usePolling = (callback: () => void, interval: number, condition: boolean) => {
  const intervalRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    if (condition) {
      intervalRef.current = setInterval(callback, interval);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [callback, interval, condition]);
};
```

### Progress Tracking
```typescript
const VideoProgressTracker: React.FC<{ jobId: string }> = ({ jobId }) => {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('pending');

  usePolling(
    async () => {
      const jobStatus = await api.get(`/api/video-jobs/${jobId}`);
      setProgress(jobStatus.data.overallProgress);
      setStatus(jobStatus.data.status);
    },
    2000,
    status === 'in_progress'
  );

  return (
    <LinearProgress 
      variant="determinate" 
      value={progress} 
      sx={{ height: 8, borderRadius: 4 }}
    />
  );
};
```

## 🚀 Performance Optimization

### Code Splitting
```typescript
// Lazy loading for pages
const CharactersPage = lazy(() => import('./pages/CharactersPage'));
const ScriptsPage = lazy(() => import('./pages/ScriptsPage'));
const VideosPage = lazy(() => import('./pages/VideosPage'));

// Suspense wrapper
<Suspense fallback={<LoadingScreen />}>
  <Routes>
    <Route path="/characters" element={<CharactersPage />} />
    <Route path="/scripts" element={<ScriptsPage />} />
    <Route path="/videos" element={<VideosPage />} />
  </Routes>
</Suspense>
```

### Memoization
```typescript
// Memoized components
const CharacterCard = React.memo<CharacterCardProps>(({ character }) => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6">{character.displayName}</Typography>
        <Typography variant="body2">{character.description}</Typography>
      </CardContent>
    </Card>
  );
});

// Memoized values
const filteredCharacters = useMemo(() => {
  return characters.filter(char => 
    char.displayName.toLowerCase().includes(searchTerm.toLowerCase())
  );
}, [characters, searchTerm]);
```

### Efficient Re-rendering
```typescript
// useCallback for event handlers
const handleCharacterSelect = useCallback((characterId: string) => {
  setSelectedCharacters(prev => 
    prev.includes(characterId) 
      ? prev.filter(id => id !== characterId)
      : [...prev, characterId]
  );
}, []);

// useMemo for expensive computations
const characterStats = useMemo(() => {
  return characters.reduce((acc, char) => {
    acc.totalStars += char.starred;
    acc.totalCharacters += 1;
    return acc;
  }, { totalStars: 0, totalCharacters: 0 });
}, [characters]);
```

## 🎯 User Experience Features

### Loading States
```typescript
const LoadingButton: React.FC<{ loading: boolean; children: React.ReactNode }> = ({ 
  loading, 
  children 
}) => (
  <Button
    disabled={loading}
    startIcon={loading ? <CircularProgress size={20} /> : null}
  >
    {children}
  </Button>
);
```

### Error Handling
```typescript
const ErrorBoundary: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [hasError, setHasError] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const handleError = (event: ErrorEvent) => {
      setHasError(true);
      setError(new Error(event.message));
    };

    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, []);

  if (hasError) {
    return (
      <Alert severity="error">
        <AlertTitle>Something went wrong</AlertTitle>
        {error?.message}
      </Alert>
    );
  }

  return <>{children}</>;
};
```

### Responsive Design
```typescript
const useResponsive = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.between('sm', 'md'));
  const isDesktop = useMediaQuery(theme.breakpoints.up('md'));

  return { isMobile, isTablet, isDesktop };
};
```

## 🔧 Development Tools

### TypeScript Configuration
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

### Vite Configuration
```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['@mui/material', '@mui/icons-material'],
        },
      },
    },
  },
});
```

## 🧪 Testing

### Component Testing
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { CharacterCard } from './CharacterCard';

describe('CharacterCard', () => {
  const mockCharacter = {
    id: '1',
    displayName: 'Test Character',
    audioFile: 'test.wav',
    images: {},
    starred: 5,
    isStarred: false,
  };

  test('renders character information', () => {
    render(<CharacterCard character={mockCharacter} />);
    
    expect(screen.getByText('Test Character')).toBeInTheDocument();
    expect(screen.getByText('5 stars')).toBeInTheDocument();
  });

  test('handles star click', () => {
    const onStar = jest.fn();
    render(<CharacterCard character={mockCharacter} onStar={onStar} />);
    
    fireEvent.click(screen.getByTestId('star-button'));
    expect(onStar).toHaveBeenCalledWith('1');
  });
});
```

### Integration Testing
```typescript
import { render, screen, waitFor } from '@testing-library/react';
import { AuthProvider } from './AuthProvider';
import { api } from '../services/api';

jest.mock('../services/api');

describe('AuthProvider', () => {
  test('loads user on mount', async () => {
    (api.get as jest.Mock).mockResolvedValue({
      data: { id: '1', name: 'Test User' }
    });

    render(
      <AuthProvider>
        <div data-testid="auth-content">Content</div>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('auth-content')).toBeInTheDocument();
    });
  });
});
```

## 📱 Mobile Optimization

### Responsive Components
```typescript
const ResponsiveGrid: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <Grid container spacing={isMobile ? 1 : 2}>
      {characters.map(character => (
        <Grid 
          item 
          xs={12} 
          sm={6} 
          md={4} 
          lg={3} 
          key={character.id}
        >
          <CharacterCard character={character} />
        </Grid>
      ))}
    </Grid>
  );
};
```

### Touch Interactions
```typescript
const SwipeableCard: React.FC = () => {
  const [swipeState, setSwipeState] = useState({ x: 0, y: 0 });

  const handleTouchStart = (e: TouchEvent) => {
    const touch = e.touches[0];
    setSwipeState({ x: touch.clientX, y: touch.clientY });
  };

  const handleTouchMove = (e: TouchEvent) => {
    if (!swipeState.x || !swipeState.y) return;
    
    const touch = e.touches[0];
    const deltaX = touch.clientX - swipeState.x;
    
    if (Math.abs(deltaX) > 50) {
      // Handle swipe action
      handleSwipe(deltaX > 0 ? 'right' : 'left');
    }
  };

  return (
    <Card
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
    >
      Card Content
    </Card>
  );
};
```

## 🚀 Deployment

### Production Build
```bash
# Build for production
npm run build

# Preview production build
npm run preview

# Analyze bundle size
npm run analyze
```

### Environment Variables
```typescript
// vite-env.d.ts
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_APP_VERSION: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
```

### Static Hosting
```bash
# Deploy to Netlify
netlify deploy --dir=dist --prod

# Deploy to Vercel
vercel --prod

# Deploy to GitHub Pages
npm run deploy
```

## 🔍 Debugging

### Development Tools
```typescript
// React DevTools integration
if (process.env.NODE_ENV === 'development') {
  const whyDidYouRender = require('@welldone-software/why-did-you-render');
  whyDidYouRender(React, {
    trackAllPureComponents: true,
  });
}
```

### Console Logging
```typescript
const useDebugValue = (value: any, label: string) => {
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.log(`[${label}]`, value);
    }
  }, [value, label]);
};
```

## 📚 Additional Resources

- **React Documentation**: https://react.dev/
- **TypeScript Handbook**: https://www.typescriptlang.org/docs/
- **Material-UI Documentation**: https://mui.com/
- **Vite Documentation**: https://vitejs.dev/
- **React Router**: https://reactrouter.com/
- **Axios Documentation**: https://axios-http.com/

## 🤝 Contributing

### Development Guidelines
1. Follow TypeScript strict mode
2. Use Material-UI components consistently
3. Implement proper error boundaries
4. Add comprehensive prop types
5. Write unit tests for components
6. Follow accessibility best practices

### Code Style
```typescript
// Use consistent naming conventions
const ComponentName: React.FC<Props> = ({ prop1, prop2 }) => {
  // Component logic
  return <div>Content</div>;
};

// Export components with proper types
export type { ComponentProps };
export { ComponentName };
```

---

**⚛️ Build Amazing User Experiences! ✨**
