import React, { useState } from 'react';
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
  AccountCircle,
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

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

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
      height: '100vh', // Fixed viewport height
      overflow: 'hidden', // Prevent scrolling on main container
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
              sx={{
                mr: 2,
                background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                width: 40,
                height: 40,
              }}
            >
              <AccountCircle />
            </Avatar>
            <Typography variant="h6" component="div" sx={{ fontWeight: 700 }}>
              Meme Maker
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
          height: '100vh', // Fixed viewport height
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden', // Prevent scrolling on main container
          ml: isSidebarCollapsed ? '73px' : '280px', // Account for sidebar width
          transition: 'margin 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        }}
      >
        {/* Content Area - Scrollable */}
        <Box
          sx={{
            flexGrow: 1,
            pt: 8, // Account for AppBar height
            overflow: 'auto', // Make this area scrollable
            background: 'transparent',
          }}
        >
          {children}
        </Box>
      </Box>
    </Box>
  );
}; 