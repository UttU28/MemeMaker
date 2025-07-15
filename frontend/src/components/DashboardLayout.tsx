import React, { useState, useEffect } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Button,
  Avatar,
  IconButton,
  Chip,
} from '@mui/material';
import {
  ExitToApp,
  Menu as MenuIcon,
  PlaylistPlay,
} from '@mui/icons-material';
import { useAuth } from '../hooks/useAuth';
import { useNavigate, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

// localStorage key for sidebar state
const SIDEBAR_STORAGE_KEY = 'memevoiceclone-inator-sidebar-collapsed';

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  // Initialize sidebar state from localStorage
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(() => {
    try {
      const saved = localStorage.getItem(SIDEBAR_STORAGE_KEY);
      return saved ? JSON.parse(saved) : false;
    } catch (error) {
      console.warn('Failed to load sidebar state from localStorage:', error);
      return false;
    }
  });

  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Save sidebar state to localStorage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem(SIDEBAR_STORAGE_KEY, JSON.stringify(isSidebarCollapsed));
    } catch (error) {
      console.warn('Failed to save sidebar state to localStorage:', error);
    }
  }, [isSidebarCollapsed]);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleTabChange = (tabId: string) => {
    navigate(`/${tabId}`);
  };

  const handleToggleSidebar = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  // Get active tab from current route
  const getActiveTab = () => {
    const path = location.pathname.slice(1); // Remove leading slash
    return path || 'profile'; // Default to profile if root
  };

  if (!isAuthenticated || !user) {
    return null;
  }

  return (
    <Box sx={{ 
      display: 'flex', 
      height: '100vh',
      overflow: 'hidden',
      position: 'relative', // Added for better positioning
    }}>
      {/* App Bar */}
      <AppBar 
        position="fixed" 
        elevation={0}
        sx={{ 
          zIndex: (theme) => theme.zIndex.drawer + 1,
          backgroundColor: 'rgba(15, 23, 42, 0.8)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(148, 163, 184, 0.1)',
          left: 0,
          right: 0,
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="toggle sidebar"
            onClick={handleToggleSidebar}
            edge="start"
            sx={{ 
              mr: 2,
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              },
            }}
          >
            <MenuIcon />
          </IconButton>
          <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
            <Avatar
              src="/doofenshmirtz-flipped.png"
              alt="Dr. Doofenshmirtz"
              sx={{
                mr: 2,
                background: '#1e293b',
                width: 40,
                height: 40,
                border: '2px solid rgba(99, 102, 241, 0.3)',
                boxShadow: '0 0 10px rgba(99, 102, 241, 0.3)',
              }}
            />
            <Typography variant="h6" component="div" sx={{ fontWeight: 700 }}>
              MemeVoiceClone-inator
            </Typography>
          </Box>
          
          {/* Token Display */}
          <Box sx={{ mr: 2 }}>
            <Chip 
              icon={<PlaylistPlay />}
              label={`${user.tokens || 0} tokens`}
              color="warning"
              size="small"
              sx={{
                fontWeight: 600,
                background: 'linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)',
                '& .MuiChip-label': {
                  px: 2,
                },
              }}
            />
          </Box>
          <Button
            color="inherit"
            onClick={handleLogout}
            startIcon={<ExitToApp />}
            sx={{ 
              textTransform: 'none',
              fontWeight: 600,
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              },
            }}
          >
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Sidebar 
        activeTab={getActiveTab()} 
        onTabChange={handleTabChange}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={handleToggleSidebar}
      />

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          height: '100vh',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          // Remove margin-left approach - let the permanent drawer handle layout
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          position: 'relative',
          boxSizing: 'border-box',
          minWidth: 0, // Prevent flex item from growing beyond container
        }}
      >
        {/* Content Area - Scrollable */}
        <Box
          sx={{
            flexGrow: 1,
            pt: 8, // Account for AppBar height (64px)
            overflow: 'auto',
            background: 'transparent',
            width: '100%',
            height: '100%',
            // Ensure proper padding and spacing
            px: 0,
            position: 'relative',
            boxSizing: 'border-box',
            // Prevent content from shifting during transitions
            minWidth: 0,
          }}
        >
          {children}
        </Box>
      </Box>
    </Box>
  );
}; 