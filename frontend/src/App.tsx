import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { AuthProvider } from './contexts/AuthProvider';
import { useAuth } from './hooks/useAuth';
import theme from './theme';
import Dashboard from './components/Dashboard';
import { ProfilePage } from './pages/ProfilePage';
import { CharactersPage } from './pages/CharactersPage';
import { ScriptsPage } from './pages/ScriptsPage';
import { VideosPage } from './pages/VideosPage';
import { AboutUsPage } from './pages/AboutUsPage';
import { FlowPage } from './pages/FlowPage';
import { AdminPage } from './pages/AdminPage';
import { Auth } from './pages/Auth';
import { LoadingScreen } from './components/LoadingScreen';

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingScreen message="Verifying your credentials..." />;
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/auth" replace />;
};

// Admin Route Component (requires admin privileges)
const AdminRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return <LoadingScreen message="Verifying your credentials..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/auth" replace />;
  }

  if (user?.subscription !== 'ADMI') {
    return <Navigate to="/profile" replace />;
  }

  return <>{children}</>;
};

// Public Route Component (redirect to profile if authenticated)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingScreen message="Loading MemeVoiceClone-inator..." />;
  }

  return isAuthenticated ? <Navigate to="/profile" replace /> : <>{children}</>;
};

// App Routes Component (needs to be inside AuthProvider)
const AppRoutes: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route 
          path="/" 
          element={
            <PublicRoute>
              <Dashboard />
            </PublicRoute>
          } 
        />
        <Route 
          path="/auth" 
          element={
            <PublicRoute>
              <Auth />
            </PublicRoute>
          } 
        />
        <Route 
          path="/profile" 
          element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/characters" 
          element={
            <ProtectedRoute>
              <CharactersPage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/scripts" 
          element={
            <ProtectedRoute>
              <ScriptsPage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/videos" 
          element={
            <ProtectedRoute>
              <VideosPage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/flow" 
          element={
            <ProtectedRoute>
              <FlowPage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/admin" 
          element={
            <AdminRoute>
              <AdminPage />
            </AdminRoute>
          } 
        />
        <Route 
          path="/about" 
          element={
            <ProtectedRoute>
              <AboutUsPage />
            </ProtectedRoute>
          } 
        />
        {/* Legacy redirect for old dashboard route */}
        <Route 
          path="/dashboard" 
          element={<Navigate to="/profile" replace />} 
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
};

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

export default App;
