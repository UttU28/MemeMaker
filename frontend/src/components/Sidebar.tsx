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
} from '@mui/icons-material';

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

const SIDEBAR_WIDTH = 280;
const SIDEBAR_COLLAPSED_WIDTH = 73;

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange, isCollapsed, onToggleCollapse }) => {

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
  ];



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
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
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
            transition: 'opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            overflow: 'hidden',
            width: isCollapsed ? 0 : 'auto',
            whiteSpace: 'nowrap',
          }}
        >
          {!isCollapsed && (
            <Typography variant="h6" sx={{ fontWeight: 700, color: 'text.primary' }}>
              Dashboard
            </Typography>
          )}
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
                    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                    justifyContent: isCollapsed ? 'center' : 'flex-start',
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
                    justifyContent: 'center',
                    mr: isCollapsed ? 0 : 2,
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <Box
                  sx={{
                    opacity: isCollapsed ? 0 : 1,
                    transition: 'opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    overflow: 'hidden',
                    width: isCollapsed ? 0 : 'auto',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {!isCollapsed && (
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
                  )}
                </Box>
              </ListItemButton>
            </Tooltip>
          </ListItem>
        ))}
      </List>

      {/* Sidebar Footer */}
      <Box
        sx={{
          opacity: isCollapsed ? 0 : 1,
          transition: 'opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          borderTop: '1px solid rgba(148, 163, 184, 0.1)',
          overflow: 'hidden',
          height: isCollapsed ? 0 : 'auto',
        }}
      >
        {!isCollapsed && (
          <Box sx={{ p: 2 }}>
            <Typography variant="caption" sx={{ color: 'text.secondary' }}>
              Meme Maker Dashboard
            </Typography>
          </Box>
        )}
      </Box>
    </Box>
  );

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: isCollapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH,
        flexShrink: 0,
        transition: 'width 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        '& .MuiDrawer-paper': {
          width: isCollapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH,
          height: '100vh',
          boxSizing: 'border-box',
          position: 'fixed',
          top: 0,
          left: 0,
          zIndex: (theme) => theme.zIndex.drawer,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
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