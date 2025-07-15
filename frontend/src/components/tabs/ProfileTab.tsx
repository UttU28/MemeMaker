import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Avatar,
  Paper,
  Divider,
  Fade,
  Card,
  CardContent,
  Skeleton,
  Alert,
  Button,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Email,
  Schedule,
  Timeline,
  Description,
  Person,
  VideoFile,
  Refresh,
  PlaylistPlay,
  YouTube,
  Launch,
  PersonAdd as PersonAddIcon,
  Create as CreateIcon,
  VideoLibrary as VideoLibraryIcon,
} from '@mui/icons-material';
import { useAuth } from '../../hooks/useAuth';
import { activityAPI, type UserActivity, type ActivityStats } from '../../services/api';

export const ProfileTab: React.FC = () => {
  const { user } = useAuth();
  const [activities, setActivities] = useState<UserActivity[]>([]);
  const [activityStats, setActivityStats] = useState<ActivityStats | null>(null);
  const [loadingActivities, setLoadingActivities] = useState(true);
  const [loadingStats, setLoadingStats] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchActivities = async () => {
    try {
      setLoadingActivities(true);
      setError(null);
      const response = await activityAPI.getMyActivities(10); // Get latest 10 activities
      setActivities(response.activities);
    } catch (err) {
      console.error('Error fetching activities:', err);
      setError('Failed to load activities');
    } finally {
      setLoadingActivities(false);
    }
  };

  const fetchActivityStats = async () => {
    try {
      setLoadingStats(true);
      const stats = await activityAPI.getMyActivityStats();
      setActivityStats(stats);
    } catch (err) {
      console.error('Error fetching activity stats:', err);
    } finally {
      setLoadingStats(false);
    }
  };



  useEffect(() => {
    if (user) {
      fetchActivities();
      fetchActivityStats();
    }
  }, [user]);

  const getActivityIcon = (type: string) => {
    if (type.includes('script')) {
      return <Description sx={{ fontSize: 16, color: 'primary.main' }} />;
    } else if (type.includes('character')) {
      return <Person sx={{ fontSize: 16, color: 'success.main' }} />;
    } else if (type.includes('video')) {
      return <VideoFile sx={{ fontSize: 16, color: 'warning.main' }} />;
    }
    return <Timeline sx={{ fontSize: 16, color: 'text.secondary' }} />;
  };

  const getActivityColor = (type: string) => {
    if (type.includes('script')) {
      return 'primary.main';
    } else if (type.includes('character')) {
      return 'success.main';
    } else if (type.includes('video')) {
      return 'warning.main';
    }
    return 'text.secondary';
  };

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (!user) {
    return null;
  }


  const userInfo = [
    {
      icon: <Email sx={{ color: 'primary.main' }} />,
      title: 'Email',
      value: user.email,
      type: 'text' as const
    },
    {
      icon: <PlaylistPlay sx={{ color: 'warning.main' }} />,
      title: 'Tokens',
      value: user.tokens || 0,
      type: 'token' as const,
      tokenCount: user.tokens || 0
    },
    {
      icon: <Schedule sx={{ color: 'primary.main' }} />,
      title: 'Member Since',
      value: new Date(user.createdAt).toLocaleDateString(),
      type: 'text' as const
    },
    {
      icon: <YouTube sx={{ color: '#ff0000' }} />,
      title: 'Subscribe My Channel',
      value: 'ThatInsaneGuy',
      type: 'youtube' as const,
      url: 'https://www.youtube.com/@ThatInsaneGuy'
    }
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Welcome Section */}
      <Fade in timeout={800}>
        <Paper 
          elevation={0} 
          sx={{ 
            p: 4, 
            mb: 4, 
            borderRadius: 3,
            background: 'rgba(30, 41, 59, 0.8)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(148, 163, 184, 0.1)',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <Avatar 
              src="/perry-platypus.png"
              alt="Perry the Platypus"
              sx={{ 
                width: 80, 
                height: 80, 
                background: '#0f172a',
                mr: 3,
                boxShadow: '0 10px 15px -3px rgba(99, 102, 241, 0.3)',
                border: '3px solid rgba(99, 102, 241, 0.4)',
                borderRadius: '16px',
              }}
            />
            <Box>
              <Typography variant="h3" sx={{ fontWeight: 800, mb: 1 }}>
                Welcome back, {user.name}!
              </Typography>
              <Typography variant="h6" sx={{ color: 'text.secondary' }}>
                Ready to create some viral memes?
              </Typography>
            </Box>
          </Box>

          <Divider sx={{ my: 3, borderColor: 'rgba(148, 163, 184, 0.1)' }} />

          {/* User Info Grid - 2x2 Layout (4 items) */}
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
              gap: 2,
            }}
          >
            {userInfo.map((info, index) => (
              <Box
                key={index}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  py: 1,
                }}
              >
                <Box sx={{ mr: 2 }}>
                  {info.icon}
                </Box>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="body1" sx={{ fontWeight: 600, color: 'text.primary', mb: 0.5 }}>
                    {info.title}
                  </Typography>
                  {info.type === 'token' ? (
                    <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                      {info.tokenCount} tokens
                    </Typography>
                  ) : info.type === 'youtube' ? (
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={<Launch />}
                      onClick={() => window.open(info.url, '_blank')}
                      sx={{
                        px: 2,
                        py: 0.5,
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        borderRadius: 1.5,
                        background: 'linear-gradient(135deg, #ff0000 0%, #cc0000 100%)',
                        color: 'white',
                        textTransform: 'none',
                        '&:hover': {
                          background: 'linear-gradient(135deg, #cc0000 0%, #990000 100%)',
                          transform: 'translateY(-1px)',
                        },
                      }}
                    >
                      Subscribe
                    </Button>
                  ) : (
                    <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                      {info.value}
                    </Typography>
                  )}
                </Box>
              </Box>
            ))}
          </Box>
        </Paper>
      </Fade>

      {/* How to Use Section */}
      <Fade in timeout={900}>
        <Paper 
          elevation={0} 
          sx={{ 
            p: 4, 
            mb: 4,
            borderRadius: 3,
            background: 'rgba(30, 41, 59, 0.8)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(148, 163, 184, 0.1)',
          }}
        >
          <Typography 
            variant="h4" 
            component="h2" 
            sx={{ 
              textAlign: 'center', 
              mb: 4,
              fontWeight: 700,
              background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}
          >
            How to Use Our Platform
          </Typography>
          
          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr' }, 
            gap: 3 
          }}>
            {[
              {
                icon: <PersonAddIcon sx={{ fontSize: 32 }} />,
                title: 'Create Characters',
                description: 'Upload voice samples and create AI characters, or star existing ones from the community',
                color: '#6366f1',
                number: '1',
              },
              {
                icon: <CreateIcon sx={{ fontSize: 32 }} />,
                title: 'Generate Scripts',
                description: 'Use AI to create natural dialogue scripts between your selected characters',
                color: '#f59e0b',
                number: '2',
              },
              {
                icon: <VideoLibraryIcon sx={{ fontSize: 32 }} />,
                title: 'Generate Videos',
                description: 'Creates audio using F5-TTS technology and generates meme-worthy videos with Minecraft backgrounds',
                color: '#8b5cf6',
                number: '3',
              },
            ].map((step, index) => (
              <Fade in timeout={1000 + index * 200} key={index}>
                <Paper 
                  elevation={0}
                  sx={{ 
                    p: 3, 
                    textAlign: 'center',
                    height: '100%',
                    transition: 'all 0.3s ease',
                    position: 'relative',
                    background: 'rgba(30, 41, 59, 0.4)',
                    border: '1px solid rgba(148, 163, 184, 0.1)',
                    borderRadius: 2,
                    '&:hover': {
                      transform: 'translateY(-8px)',
                      boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
                    }
                  }}
                >
                  <Box sx={{ position: 'relative', mb: 2 }}>
                    <Avatar 
                      sx={{ 
                        mx: 'auto',
                        width: 56, 
                        height: 56,
                        background: `linear-gradient(135deg, ${step.color} 0%, ${step.color}CC 100%)`,
                        mb: 1,
                      }}
                    >
                      {step.icon}
                    </Avatar>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        fontWeight: 700,
                        color: step.color,
                        position: 'absolute',
                        top: -10,
                        right: 'calc(50% - 40px)',
                        background: 'rgba(30, 41, 59, 0.9)',
                        borderRadius: '50%',
                        width: 24,
                        height: 24,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '0.875rem',
                        border: `2px solid ${step.color}`,
                      }}
                    >
                      {step.number}
                    </Typography>
                  </Box>
                  <Typography variant="h6" sx={{ mb: 1.5, fontWeight: 600 }}>
                    {step.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.5 }}>
                    {step.description}
                  </Typography>
                </Paper>
              </Fade>
            ))}
          </Box>
        </Paper>
      </Fade>

      {/* Activity Card */}
      <Fade in timeout={1000}>
        <Paper 
          elevation={0} 
          sx={{ 
            p: 3, 
            mb: 4, 
            borderRadius: 3,
            background: 'rgba(30, 41, 59, 0.8)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(148, 163, 184, 0.1)',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2.5 }}>
            <Typography variant="h5" sx={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
              <PlaylistPlay sx={{ color: 'primary.main', fontSize: 24 }} />
              Recent Activity
            </Typography>
            <Tooltip title="Refresh Activities">
              <IconButton 
                onClick={fetchActivities}
                disabled={loadingActivities}
                size="small"
                sx={{ 
                  color: 'primary.main',
                  '&:hover': { backgroundColor: 'rgba(99, 102, 241, 0.1)' }
                }}
              >
                <Refresh />
              </IconButton>
            </Tooltip>
          </Box>

          {/* Activity Stats */}
          {loadingStats ? (
            <Box sx={{ display: 'flex', gap: 2, mb: 2.5 }}>
              {Array.from({ length: 4 }).map((_, idx) => (
                <Card key={idx} sx={{ flex: 1, background: 'rgba(99, 102, 241, 0.1)', border: '1px solid rgba(99, 102, 241, 0.2)', borderRadius: 2 }}>
                  <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                    <Skeleton variant="text" width={60} height={16} />
                    <Skeleton variant="text" width={30} height={24} />
                  </CardContent>
                </Card>
              ))}
            </Box>
          ) : activityStats && (
            <Box sx={{ display: 'flex', gap: 2, mb: 2.5 }}>
              <Card sx={{ flex: 1, background: 'rgba(99, 102, 241, 0.1)', border: '1px solid rgba(99, 102, 241, 0.2)', borderRadius: 2 }}>
                <CardContent sx={{ p: 1.5, textAlign: 'center', '&:last-child': { pb: 1.5 } }}>
                  <Typography variant="caption" sx={{ color: 'primary.main', fontWeight: 600, fontSize: '0.75rem' }}>
                    Scripts
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 700, color: 'primary.main', lineHeight: 1.2 }}>
                    {activityStats.scriptActivities}
                  </Typography>
                </CardContent>
              </Card>
              <Card sx={{ flex: 1, background: 'rgba(76, 175, 80, 0.1)', border: '1px solid rgba(76, 175, 80, 0.2)', borderRadius: 2 }}>
                <CardContent sx={{ p: 1.5, textAlign: 'center', '&:last-child': { pb: 1.5 } }}>
                  <Typography variant="caption" sx={{ color: 'success.main', fontWeight: 600, fontSize: '0.75rem' }}>
                    Characters
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 700, color: 'success.main', lineHeight: 1.2 }}>
                    {activityStats.characterActivities}
                  </Typography>
                </CardContent>
              </Card>
              <Card sx={{ flex: 1, background: 'rgba(255, 152, 0, 0.1)', border: '1px solid rgba(255, 152, 0, 0.2)', borderRadius: 2 }}>
                <CardContent sx={{ p: 1.5, textAlign: 'center', '&:last-child': { pb: 1.5 } }}>
                  <Typography variant="caption" sx={{ color: 'warning.main', fontWeight: 600, fontSize: '0.75rem' }}>
                    Videos
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 700, color: 'warning.main', lineHeight: 1.2 }}>
                    {activityStats.videoActivities}
                  </Typography>
                </CardContent>
              </Card>
              <Card sx={{ flex: 1, background: 'rgba(148, 163, 184, 0.1)', border: '1px solid rgba(148, 163, 184, 0.2)', borderRadius: 2 }}>
                <CardContent sx={{ p: 1.5, textAlign: 'center', '&:last-child': { pb: 1.5 } }}>
                  <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600, fontSize: '0.75rem' }}>
                    Total
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 700, lineHeight: 1.2 }}>
                    {activityStats.totalActivities}
                  </Typography>
                </CardContent>
              </Card>
            </Box>
          )}

          <Divider sx={{ my: 2, borderColor: 'rgba(148, 163, 184, 0.1)' }} />

          {/* Activity List */}
          {error && (
            <Alert 
              severity="error" 
              sx={{ mb: 3 }}
              action={
                <Button color="inherit" size="small" onClick={fetchActivities}>
                  Retry
                </Button>
              }
            >
              {error}
            </Alert>
          )}

          {loadingActivities ? (
            <Box>
              {Array.from({ length: 5 }).map((_, idx) => (
                <Box key={idx} sx={{ display: 'flex', alignItems: 'center', py: 1.5, borderBottom: '1px solid rgba(148, 163, 184, 0.1)' }}>
                  <Skeleton variant="circular" width={32} height={32} sx={{ mr: 1.5 }} />
                  <Box sx={{ flex: 1 }}>
                    <Skeleton variant="text" width="70%" height={18} />
                    <Skeleton variant="text" width="40%" height={14} />
                  </Box>
                </Box>
              ))}
            </Box>
          ) : activities.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 3 }}>
              <Timeline sx={{ fontSize: 40, color: 'text.secondary', mb: 1.5 }} />
              <Typography variant="subtitle1" sx={{ color: 'text.secondary', mb: 1, fontWeight: 600 }}>
                No Recent Activity
              </Typography>
              <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                Your activity will appear here as you use the platform
              </Typography>
            </Box>
          ) : (
            <Box>
              {activities.map((activity, index) => (
                <Box 
                  key={activity.id} 
                  sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    py: 1.5, 
                    borderBottom: index < activities.length - 1 ? '1px solid rgba(148, 163, 184, 0.1)' : 'none'
                  }}
                >
                  <Box sx={{ 
                    width: 32, 
                    height: 32, 
                    borderRadius: '50%', 
                    background: `linear-gradient(135deg, ${getActivityColor(activity.type)}20 0%, ${getActivityColor(activity.type)}10 100%)`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mr: 1.5,
                    border: `1px solid ${getActivityColor(activity.type)}40`
                  }}>
                    {getActivityIcon(activity.type)}
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: 'text.primary', lineHeight: 1.3 }}>
                      {activity.message}
                    </Typography>
                    <Typography variant="caption" sx={{ color: 'text.secondary', mt: 0.25, display: 'block' }}>
                      {formatDate(activity.timestamp)}
                    </Typography>
                  </Box>
                </Box>
              ))}
              
              {activities.length >= 10 && (
                <Box sx={{ textAlign: 'center', mt: 2 }}>
                  <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                    Showing recent 10 activities
                  </Typography>
                </Box>
              )}
            </Box>
          )}
        </Paper>
      </Fade>
    </Container>
  );
}; 