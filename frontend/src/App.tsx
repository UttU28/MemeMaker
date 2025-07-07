import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { AuthProvider } from './contexts/AuthProvider';
import { useAuth } from './hooks/useAuth';
import theme from './theme';
import Dashboard from './components/Dashboard';
import { DashboardLayout } from './components/DashboardLayout';
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

// Public Route Component (redirect to profile if authenticated)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingScreen message="Loading Meme Maker..." />;
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
              <DashboardLayout />
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
