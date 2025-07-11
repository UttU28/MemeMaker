import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Avatar,
  Chip,
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
  AccountCircle,
  Email,
  Verified,
  Star,
  Schedule,
  Timeline,
  Description,
  Person,
  VideoFile,
  Refresh,
  PlaylistPlay,
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
      icon: <Verified sx={{ color: 'primary.main' }} />,
      title: 'Account Status',
      value: user.isVerified ? 'Verified' : 'Unverified',
      type: 'chip' as const,
      chipColor: (user.isVerified ? 'success' : 'warning') as 'success' | 'warning'
    },
    {
      icon: <Star sx={{ color: 'primary.main' }} />,
      title: 'Subscription',
      value: user.subscription || 'Free',
      type: 'chip' as const,
      chipColor: 'primary' as const
    },
    {
      icon: <Schedule sx={{ color: 'primary.main' }} />,
      title: 'Member Since',
      value: new Date(user.createdAt).toLocaleDateString(),
      type: 'text' as const
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
              sx={{ 
                width: 80, 
                height: 80, 
                background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                mr: 3,
                boxShadow: '0 10px 15px -3px rgba(99, 102, 241, 0.3)',
              }}
            >
              <AccountCircle sx={{ fontSize: 50 }} />
            </Avatar>
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

          {/* User Info Grid - 2x2 Layout */}
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
                  {info.type === 'chip' ? (
                    <Chip 
                      label={info.value} 
                      color={info.chipColor}
                      size="small"
                      sx={{
                        fontWeight: 600,
                        ...(info.chipColor === 'primary' && {
                          background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                        }),
                        '& .MuiChip-label': {
                          px: 2,
                        },
                      }}
                    />
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