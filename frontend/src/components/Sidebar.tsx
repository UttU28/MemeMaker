import React from 'react';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Typography,
  Tooltip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Person as PersonIcon,
  People as PeopleIcon,
  Description as ScriptIcon,
  VideoLibrary as VideoIcon,
  ChevronLeft as ChevronLeftIcon,
  Info as InfoIcon,
  AdminPanelSettings as AdminIcon,
  AccountTree as FlowIcon,
} from '@mui/icons-material';
import { useAuth } from '../hooks/useAuth';

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

// Consistent width constants (same as DashboardLayout)
export const SIDEBAR_WIDTH = 280;
export const SIDEBAR_COLLAPSED_WIDTH = 73;

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange, isCollapsed, onToggleCollapse }) => {
  const { user } = useAuth();

  // Check if user has admin privileges
  const isAdmin = user?.subscription === 'ADMI';

  const menuItems = [
    {
      id: 'profile',
      label: 'Profile',
      icon: <PersonIcon />,
    },
    {
      id: 'characters',
      label: 'Characters',
      icon: <PeopleIcon />,
    },
    {
      id: 'scripts',
      label: 'Scripts',
      icon: <ScriptIcon />,
    },
    {
      id: 'videos',
      label: 'Videos',
      icon: <VideoIcon />,
    },
    {
      id: 'flow',
      label: 'Flow',
      icon: <FlowIcon />,
    },
  ];

  const adminItem = {
    id: 'admin',
    label: 'Admin',
    icon: <AdminIcon />,
  };

  const aboutUsItem = {
    id: 'about',
    label: 'About Us',
    icon: <InfoIcon />,
  };

  const sidebarContent = (
    <Box
      sx={{
        width: isCollapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH,
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        background: 'rgba(15, 23, 42, 0.95)',
        backdropFilter: 'blur(20px)',
        borderRight: '1px solid rgba(148, 163, 184, 0.1)',
        transition: 'width 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        overflow: 'hidden',
      }}
    >
      {/* Sidebar Header */}
      <Box
        sx={{
          p: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: isCollapsed ? 'center' : 'space-between',
          borderBottom: '1px solid rgba(148, 163, 184, 0.1)',
        }}
      >
        <Box
          sx={{
            opacity: isCollapsed ? 0 : 1,
            transform: isCollapsed ? 'translateX(-10px)' : 'translateX(0)',
            transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
            overflow: 'hidden',
            width: isCollapsed ? 0 : 'auto',
            whiteSpace: 'nowrap',
          }}
        >
          <Typography variant="h6" sx={{ fontWeight: 700, color: 'text.primary' }}>
            Dashboard
          </Typography>
        </Box>
        <IconButton
          onClick={onToggleCollapse}
          sx={{
            color: 'text.secondary',
            '&:hover': {
              color: 'primary.main',
              backgroundColor: 'rgba(99, 102, 241, 0.1)',
            },
          }}
        >
          {isCollapsed ? <MenuIcon /> : <ChevronLeftIcon />}
        </IconButton>
      </Box>

      {/* Menu Items */}
      <List sx={{ flex: 1, px: 1, py: 2 }}>
        {menuItems.map((item) => (
          <ListItem key={item.id} disablePadding sx={{ mb: 1 }}>
            <Tooltip
              title={isCollapsed ? item.label : ''}
              placement="right"
              arrow
            >
              <ListItemButton
                selected={activeTab === item.id}
                onClick={() => onTabChange(item.id)}
                sx={{
                  borderRadius: 2,
                  minHeight: 48,
                  px: isCollapsed ? 1.5 : 2,
                  py: 1.5,
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  justifyContent: 'flex-start',
                  '&:hover': {
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    transform: isCollapsed ? 'scale(1.05)' : 'translateX(4px)',
                  },
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(99, 102, 241, 0.2)',
                    borderLeft: isCollapsed ? 'none' : '3px solid #6366f1',
                    border: isCollapsed ? '2px solid #6366f1' : 'none',
                    '&:hover': {
                      backgroundColor: 'rgba(99, 102, 241, 0.25)',
                    },
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: isCollapsed ? 'auto' : 40,
                    color: activeTab === item.id ? 'primary.main' : 'text.secondary',
                    justifyContent: isCollapsed ? 'center' : 'flex-start',
                    mr: isCollapsed ? 0 : 2,
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    transitionDelay: isCollapsed ? '0.15s' : '0s', // Delay centering when collapsing
                    width: isCollapsed ? '100%' : 'auto',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <Box
                  sx={{
                    opacity: isCollapsed ? 0 : 1,
                    transform: isCollapsed ? 'translateX(-10px)' : 'translateX(0)',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    overflow: 'hidden',
                    width: isCollapsed ? 0 : 'auto',
                    whiteSpace: 'nowrap',
                    pointerEvents: isCollapsed ? 'none' : 'auto',
                  }}
                >
                  <ListItemText
                    primary={item.label}
                    sx={{
                      margin: 0,
                      '& .MuiListItemText-primary': {
                        fontWeight: activeTab === item.id ? 600 : 500,
                        color: activeTab === item.id ? 'primary.main' : 'text.primary',
                        fontSize: '0.9rem',
                        lineHeight: 1.2,
                      },
                    }}
                  />
                </Box>
              </ListItemButton>
            </Tooltip>
          </ListItem>
        ))}
      </List>

      {/* Admin and About Us Section - Bottom */}
      <Box sx={{ px: 1, pb: 2 }}>
        {/* Admin Item - Only show for admin users */}
        {isAdmin && (
          <ListItem disablePadding sx={{ mb: 1 }}>
            <Tooltip
              title={isCollapsed ? adminItem.label : ''}
              placement="right"
              arrow
            >
              <ListItemButton
                selected={activeTab === adminItem.id}
                onClick={() => onTabChange(adminItem.id)}
                sx={{
                  borderRadius: 2,
                  minHeight: 48,
                  px: isCollapsed ? 1.5 : 2,
                  py: 1.5,
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  justifyContent: 'flex-start',
                  '&:hover': {
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    transform: isCollapsed ? 'scale(1.05)' : 'translateX(4px)',
                  },
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(99, 102, 241, 0.2)',
                    borderLeft: isCollapsed ? 'none' : '3px solid #6366f1',
                    border: isCollapsed ? '2px solid #6366f1' : 'none',
                    '&:hover': {
                      backgroundColor: 'rgba(99, 102, 241, 0.25)',
                    },
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: isCollapsed ? 'auto' : 40,
                    color: activeTab === adminItem.id ? 'primary.main' : 'text.secondary',
                    justifyContent: isCollapsed ? 'center' : 'flex-start',
                    mr: isCollapsed ? 0 : 2,
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    transitionDelay: isCollapsed ? '0.15s' : '0s', // Delay centering when collapsing
                    width: isCollapsed ? '100%' : 'auto',
                  }}
                >
                  {adminItem.icon}
                </ListItemIcon>
                <Box
                  sx={{
                    opacity: isCollapsed ? 0 : 1,
                    transform: isCollapsed ? 'translateX(-10px)' : 'translateX(0)',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    overflow: 'hidden',
                    width: isCollapsed ? 0 : 'auto',
                    whiteSpace: 'nowrap',
                    pointerEvents: isCollapsed ? 'none' : 'auto',
                  }}
                >
                  <ListItemText
                    primary={adminItem.label}
                    sx={{
                      margin: 0,
                      '& .MuiListItemText-primary': {
                        fontWeight: activeTab === adminItem.id ? 600 : 500,
                        color: activeTab === adminItem.id ? 'primary.main' : 'text.primary',
                        fontSize: '0.9rem',
                        lineHeight: 1.2,
                      },
                    }}
                  />
                </Box>
              </ListItemButton>
            </Tooltip>
          </ListItem>
        )}

        {/* About Us Item */}
        <ListItem disablePadding sx={{ mb: 1 }}>
          <Tooltip
            title={isCollapsed ? aboutUsItem.label : ''}
            placement="right"
            arrow
          >
            <ListItemButton
              selected={activeTab === aboutUsItem.id}
              onClick={() => onTabChange(aboutUsItem.id)}
              sx={{
                borderRadius: 2,
                minHeight: 48,
                px: isCollapsed ? 1.5 : 2,
                py: 1.5,
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                justifyContent: 'flex-start',
                '&:hover': {
                  backgroundColor: 'rgba(99, 102, 241, 0.1)',
                  transform: isCollapsed ? 'scale(1.05)' : 'translateX(4px)',
                },
                '&.Mui-selected': {
                  backgroundColor: 'rgba(99, 102, 241, 0.2)',
                  borderLeft: isCollapsed ? 'none' : '3px solid #6366f1',
                  border: isCollapsed ? '2px solid #6366f1' : 'none',
                  '&:hover': {
                    backgroundColor: 'rgba(99, 102, 241, 0.25)',
                  },
                },
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: isCollapsed ? 'auto' : 40,
                  color: activeTab === aboutUsItem.id ? 'primary.main' : 'text.secondary',
                  justifyContent: isCollapsed ? 'center' : 'flex-start',
                  mr: isCollapsed ? 0 : 2,
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  transitionDelay: isCollapsed ? '0.15s' : '0s', // Delay centering when collapsing
                  width: isCollapsed ? '100%' : 'auto',
                }}
              >
                {aboutUsItem.icon}
              </ListItemIcon>
              <Box
                sx={{
                  opacity: isCollapsed ? 0 : 1,
                  transform: isCollapsed ? 'translateX(-10px)' : 'translateX(0)',
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  overflow: 'hidden',
                  width: isCollapsed ? 0 : 'auto',
                  whiteSpace: 'nowrap',
                  pointerEvents: isCollapsed ? 'none' : 'auto',
                }}
              >
                <ListItemText
                  primary={aboutUsItem.label}
                  sx={{
                    margin: 0,
                    '& .MuiListItemText-primary': {
                      fontWeight: activeTab === aboutUsItem.id ? 600 : 500,
                      color: activeTab === aboutUsItem.id ? 'primary.main' : 'text.primary',
                      fontSize: '0.9rem',
                      lineHeight: 1.2,
                    },
                  }}
                />
              </Box>
            </ListItemButton>
          </Tooltip>
        </ListItem>
      </Box>
    </Box>
  );

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: isCollapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH,
        flexShrink: 0,
        transition: 'width 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        '& .MuiDrawer-paper': {
          width: isCollapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH,
          height: '100vh',
          boxSizing: 'border-box',
          position: 'fixed',
          top: 0,
          left: 0,
          zIndex: (theme) => theme.zIndex.drawer,
          transition: 'width 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
          border: 'none',
          background: 'transparent',
          overflow: 'hidden',
        },
      }}
    >
      {sidebarContent}
    </Drawer>
  );
}; 