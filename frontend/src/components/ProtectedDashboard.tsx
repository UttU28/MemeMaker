import React from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  AppBar,
  Toolbar,
  Button,
  Avatar,
  Chip,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import {
  AccountCircle,
  Email,
  Verified,
  Star,
  ExitToApp,
  Upload,
  Edit,
  Share,
  Download,
  Timeline,
  TrendingUp,
} from '@mui/icons-material';
import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';

export const ProtectedDashboard: React.FC = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  if (!isAuthenticated || !user) {
    return null;
  }

  const features = [
    {
      title: 'Upload & Edit',
      description: 'Upload images and add text to create memes',
      icon: <Upload />,
      color: '#e3f2fd',
    },
    {
      title: 'Smart Text',
      description: 'AI-powered text suggestions and formatting',
      icon: <Edit />,
      color: '#f3e5f5',
    },
    {
      title: 'Share & Export',
      description: 'Export in multiple formats and share easily',
      icon: <Share />,
      color: '#e8f5e8',
    },
    {
      title: 'Download',
      description: 'Save your memes in high quality',
      icon: <Download />,
      color: '#fff3e0',
    },
    {
      title: 'Analytics',
      description: 'Track your meme performance and engagement',
      icon: <Timeline />,
      color: '#fce4ec',
    },
    {
      title: 'Trending',
      description: 'Discover trending meme templates and styles',
      icon: <TrendingUp />,
      color: '#e0f2f1',
    },
  ];

  return (
    <Box sx={{ flexGrow: 1, minHeight: '100vh', bgcolor: '#f5f5f5' }}>
      {/* App Bar */}
      <AppBar position="static" elevation={0} sx={{ bgcolor: '#1976d2' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            Meme Maker - Dashboard
          </Typography>
          <Button
            color="inherit"
            onClick={handleLogout}
            startIcon={<ExitToApp />}
            sx={{ textTransform: 'none' }}
          >
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Welcome Section */}
        <Paper elevation={2} sx={{ p: 3, mb: 4, borderRadius: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <Avatar sx={{ width: 60, height: 60, bgcolor: '#1976d2', mr: 2 }}>
              <AccountCircle sx={{ fontSize: 40 }} />
            </Avatar>
            <Box>
              <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                Welcome back, {user.name}!
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Ready to create some viral memes?
              </Typography>
            </Box>
          </Box>

          <Divider sx={{ my: 2 }} />

          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <List>
                <ListItem>
                  <ListItemIcon>
                    <Email color="primary" />
                  </ListItemIcon>
                  <ListItemText primary="Email" secondary={user.email} />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Verified color="primary" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Account Status" 
                    secondary={
                      <Chip 
                        label={user.isVerified ? 'Verified' : 'Unverified'} 
                        color={user.isVerified ? 'success' : 'warning'}
                        size="small"
                      />
                    }
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Star color="primary" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Subscription" 
                    secondary={
                      <Chip 
                        label={user.subscription || 'Free'} 
                        color="primary"
                        size="small"
                      />
                    }
                  />
                </ListItem>
              </List>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper elevation={1} sx={{ p: 2, bgcolor: 'primary.main', color: 'white' }}>
                <Typography variant="h6" sx={{ mb: 1 }}>
                  Quick Stats
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  Member since: {new Date(user.createdAt).toLocaleDateString()}
                </Typography>
                <Typography variant="body2">
                  Last updated: {new Date(user.updatedAt).toLocaleDateString()}
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </Paper>

        {/* Features Section */}
        <Typography variant="h5" sx={{ mb: 3, fontWeight: 'bold' }}>
          Available Features
        </Typography>

        <Grid container spacing={3}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card 
                elevation={2} 
                sx={{ 
                  height: '100%',
                  borderRadius: 2,
                  transition: 'all 0.3s ease',
                  cursor: 'pointer',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
                  }
                }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Box 
                      sx={{ 
                        p: 1, 
                        borderRadius: 1, 
                        bgcolor: feature.color,
                        color: 'primary.main',
                        mr: 2
                      }}
                    >
                      {feature.icon}
                    </Box>
                    <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                      {feature.title}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Call to Action */}
        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Paper elevation={2} sx={{ p: 4, borderRadius: 2 }}>
            <Typography variant="h5" sx={{ mb: 2, fontWeight: 'bold' }}>
              Ready to Create Your First Meme?
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              Use our powerful tools to create engaging memes that will go viral!
            </Typography>
            <Button
              variant="contained"
              size="large"
              sx={{
                px: 4,
                py: 1.5,
                background: 'linear-gradient(45deg, #667eea, #764ba2)',
                '&:hover': {
                  background: 'linear-gradient(45deg, #5a67d8, #6b46c1)',
                },
                fontWeight: 'bold',
                textTransform: 'none',
              }}
            >
              Start Creating Now
            </Button>
          </Paper>
        </Box>
      </Container>
    </Box>
  );
}; 