import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  IconButton,
  Alert,
  Snackbar,
  Tooltip,
  LinearProgress,
  Skeleton,
  Fade,
  Avatar,
  Divider,
  Stack,
  Container,
  Badge,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  People as PeopleIcon,
  VideoLibrary as VideoIcon,
  Description as ScriptIcon,
  Computer as SystemIcon,
  Schedule as ScheduleIcon,
  AccessTime as AccessTimeIcon,
  BarChart as BarChartIcon,
  Assignment as AssignmentIcon,
  PlayArrow as PlayArrowIcon,
  Pause as PauseIcon,
} from '@mui/icons-material';
import { DashboardLayout } from '../components/DashboardLayout';
import { 
  adminAPI, 
  type SystemStatus, 
  type ServiceStatus, 
  type VideoQueueStatus, 
  type AdminStats, 
  type RecentUser, 
  type SystemAlert 
} from '../services/api';

interface DashboardData {
  systemStatus: SystemStatus | null;
  f5ttsStatus: ServiceStatus | null;
  ffmpegStatus: ServiceStatus | null;
  queueStatus: VideoQueueStatus | null;
  adminStats: AdminStats | null;
  recentUsers: RecentUser[];
  systemAlerts: SystemAlert[];
}

interface AnimatedCounterProps {
  value: number;
  duration?: number;
  formatter?: (value: number) => string;
}

const AnimatedCounter: React.FC<AnimatedCounterProps> = ({ 
  value, 
  duration = 2000,
  formatter = (v) => v.toLocaleString()
}) => {
  const [displayValue, setDisplayValue] = useState(0);
  const [hasAnimated, setHasAnimated] = useState(false);

  useEffect(() => {
    if (value && !hasAnimated) {
      setHasAnimated(true);
      const startTime = Date.now();
      const startValue = 0;
      
      const updateValue = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const easeOutCubic = 1 - Math.pow(1 - progress, 3);
        const currentValue = Math.floor(startValue + (value - startValue) * easeOutCubic);
        
        setDisplayValue(currentValue);
        
        if (progress < 1) {
          requestAnimationFrame(updateValue);
        }
      };
      
      requestAnimationFrame(updateValue);
    }
  }, [value, duration, hasAnimated]);

  return <span>{formatter(displayValue)}</span>;
};

// Modern Card Component
const ModernCard: React.FC<{ 
  children: React.ReactNode; 
  title?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  elevation?: number;
  sx?: object;
}> = ({ children, title, icon, action, elevation = 0, sx = {} }) => {
  return (
    <Card
      elevation={elevation}
      sx={{
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: 3,
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
        },
        ...sx,
      }}
    >
      {title && (
        <>
          <Box sx={{ p: 3, pb: 1 }}>
            <Stack direction="row" alignItems="center" justifyContent="space-between">
              <Stack direction="row" alignItems="center" spacing={2}>
                {icon && (
                  <Box
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: 2,
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                    }}
                  >
                    {icon}
                  </Box>
                )}
                <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                  {title}
                </Typography>
              </Stack>
              {action}
            </Stack>
          </Box>
          <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.1)' }} />
        </>
      )}
      <CardContent sx={{ p: 3 }}>
        {children}
      </CardContent>
    </Card>
  );
};


// Status Indicator Component
const StatusIndicator: React.FC<{ 
  status: string; 
  label: string;
  description?: string;
}> = ({ status, label, description }) => {
  const getStatusColor = () => {
    switch (status?.toLowerCase()) {
      case 'connected':
      case 'active':
      case 'available':
        return '#22c55e';
      case 'disconnected':
      case 'error':
      case 'not_found':
        return '#ef4444';
      default:
        return '#f59e0b';
    }
  };

  const color = getStatusColor();

  return (
    <Stack direction="row" alignItems="center" spacing={2} sx={{ py: 1 }}>
      <Box
        sx={{
          width: 12,
          height: 12,
          borderRadius: '50%',
          backgroundColor: color,
          boxShadow: `0 0 8px ${color}50`,
          animation: status === 'active' || status === 'connected' ? 'pulse 2s infinite' : 'none',
          '@keyframes pulse': {
            '0%': { opacity: 1 },
            '50%': { opacity: 0.5 },
            '100%': { opacity: 1 },
          },
        }}
      />
      <Box sx={{ flex: 1 }}>
        <Typography variant="body2" sx={{ color: 'white', fontWeight: 500 }}>
          {label}
        </Typography>
        {description && (
          <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
            {description}
          </Typography>
        )}
      </Box>
      <Chip
        label={status}
        size="small"
        sx={{
          backgroundColor: `${color}20`,
          color: color,
          border: `1px solid ${color}40`,
          fontWeight: 600,
          textTransform: 'capitalize',
        }}
      />
    </Stack>
  );
};

export const AdminPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [data, setData] = useState<DashboardData>({
    systemStatus: null,
    f5ttsStatus: null,
    ffmpegStatus: null,
    queueStatus: null,
    adminStats: null,
    recentUsers: [],
    systemAlerts: [],
  });
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'warning' | 'info';
  }>({
    open: false,
    message: '',
    severity: 'info',
  });

  const fetchAllData = async () => {
    try {
      const [
        systemStatus,
        f5ttsStatus,
        ffmpegStatus,
        queueStatus,
        adminStats,
        recentUsers,
        systemAlerts,
      ] = await Promise.all([
        adminAPI.getSystemStatus(),
        adminAPI.getF5TTSStatus(),
        adminAPI.getFFmpegStatus(),
        adminAPI.getVideoQueueStatus(),
        adminAPI.getAdminStats(),
        adminAPI.getRecentUsers(5),
        adminAPI.getSystemAlerts(5),
      ]);

      setData({
        systemStatus,
        f5ttsStatus,
        ffmpegStatus,
        queueStatus,
        adminStats,
        recentUsers,
        systemAlerts,
      });
    } catch (error) {
      console.error('Failed to fetch admin data:', error);
      setSnackbar({
        open: true,
        message: 'Failed to fetch admin data',
        severity: 'error',
      });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchAllData();
  };

  useEffect(() => {
    fetchAllData();
    
    const interval = setInterval(() => {
      if (!refreshing) {
        fetchAllData();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [refreshing]);

  const formatTimeAgo = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diff = now.getTime() - date.getTime();
      const minutes = Math.floor(diff / 60000);
      
      if (minutes < 1) return 'Just now';
      if (minutes < 60) return `${minutes}m ago`;
      if (minutes < 1440) return `${Math.floor(minutes / 60)}h ago`;
      return `${Math.floor(minutes / 1440)}d ago`;
    } catch {
      return 'Unknown';
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <Box
          sx={{
            p: 4,
            background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
            minHeight: '100vh',
          }}
        >
          <Container maxWidth="xl">
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              {[...Array(4)].map((_, index) => (
                <Skeleton
                  key={index}
                  variant="rectangular"
                  height={160}
                  sx={{
                    borderRadius: 3,
                    bgcolor: 'rgba(255, 255, 255, 0.05)',
                  }}
                />
              ))}
            </Box>
          </Container>
        </Box>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <Box
        sx={{
          background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
          minHeight: '100vh',
          py: 4,
        }}
      >
        <Container maxWidth="xl">
          {/* Header */}
          <Fade in timeout={600}>
            <Box sx={{ mb: 6 }}>
              <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
                <Box>
                  <Typography
                    variant="h3"
                    component="h1"
                    sx={{
                      fontWeight: 800,
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      backgroundClip: 'text',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      mb: 1,
                    }}
                  >
                    Admin Dashboard
                  </Typography>
                  <Typography
                    variant="h6"
                    sx={{ color: 'rgba(255, 255, 255, 0.7)', fontWeight: 400 }}
                  >
                    Real-time system monitoring & analytics
                  </Typography>
                </Box>
                
                <Stack direction="row" alignItems="center" spacing={2}>
                  <Chip
                    icon={<ScheduleIcon />}
                    label="Live"
                    variant="outlined"
                    sx={{
                      color: '#22c55e',
                      borderColor: '#22c55e',
                      '& .MuiChip-icon': { color: '#22c55e' },
                    }}
                  />
                  <Tooltip title="Refresh all data">
                    <IconButton
                      onClick={handleRefresh}
                      disabled={refreshing}
                      sx={{
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        color: 'white',
                        '&:hover': {
                          background: 'linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%)',
                          transform: 'scale(1.05)',
                        },
                        transition: 'all 0.2s ease',
                      }}
                    >
                      <RefreshIcon 
                        sx={{ 
                          animation: refreshing ? 'spin 1s linear infinite' : 'none',
                          '@keyframes spin': {
                            '0%': { transform: 'rotate(0deg)' },
                            '100%': { transform: 'rotate(360deg)' },
                          },
                        }} 
                      />
                    </IconButton>
                  </Tooltip>
                </Stack>
              </Stack>
            </Box>
          </Fade>

          {/* ROW 1: KEY METRICS - FULL WIDTH */}
          <Box sx={{ mb: 4 }}>
            <ModernCard
              title="Key Metrics"
              icon={<BarChartIcon />}
              action={
                <Chip
                  label="Live Data"
                  size="small"
                  sx={{
                    backgroundColor: 'rgba(59, 130, 246, 0.2)',
                    color: '#3b82f6',
                    border: '1px solid rgba(59, 130, 246, 0.3)',
                  }}
                />
              }
            >
              <Box sx={{ display: 'flex', justifyContent: 'space-around', gap: 3 }}>
                {/* Total Users */}
                <Box sx={{ textAlign: 'center', flex: 1 }}>
                  <Box
                    sx={{
                      width: 64,
                      height: 64,
                      borderRadius: 3,
                      background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                      margin: '0 auto 16px auto',
                      boxShadow: '0 8px 32px rgba(59, 130, 246, 0.3)',
                    }}
                  >
                    <PeopleIcon sx={{ fontSize: 32 }} />
                  </Box>
                  <Typography variant="h3" sx={{ color: 'white', fontWeight: 800, mb: 1 }}>
                    <AnimatedCounter value={data.adminStats?.totalUsers || 0} />
                  </Typography>
                  <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.8)', mb: 1, fontWeight: 500 }}>
                    Total Users
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#22c55e', fontWeight: 600 }}>
                    Today: +<AnimatedCounter value={data.adminStats?.newUsersToday || 0} />
                  </Typography>
                </Box>

                {/* Characters */}
                <Box sx={{ textAlign: 'center', flex: 1 }}>
                  <Box
                    sx={{
                      width: 64,
                      height: 64,
                      borderRadius: 3,
                      background: 'linear-gradient(135deg, #8b5cf6, #7c3aed)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                      margin: '0 auto 16px auto',
                      boxShadow: '0 8px 32px rgba(139, 92, 246, 0.3)',
                    }}
                  >
                    <AssignmentIcon sx={{ fontSize: 32 }} />
                  </Box>
                  <Typography variant="h3" sx={{ color: 'white', fontWeight: 800, mb: 1 }}>
                    <AnimatedCounter value={data.adminStats?.totalCharacters || 0} />
                  </Typography>
                  <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.8)', mb: 1, fontWeight: 500 }}>
                    Characters
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#8b5cf6', fontWeight: 600 }}>
                    Today: +<AnimatedCounter value={data.adminStats?.charactersCreatedToday || 0} />
                  </Typography>
                </Box>

                {/* Scripts */}
                <Box sx={{ textAlign: 'center', flex: 1 }}>
                  <Box
                    sx={{
                      width: 64,
                      height: 64,
                      borderRadius: 3,
                      background: 'linear-gradient(135deg, #06b6d4, #0891b2)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                      margin: '0 auto 16px auto',
                      boxShadow: '0 8px 32px rgba(6, 182, 212, 0.3)',
                    }}
                  >
                    <ScriptIcon sx={{ fontSize: 32 }} />
                  </Box>
                  <Typography variant="h3" sx={{ color: 'white', fontWeight: 800, mb: 1 }}>
                    <AnimatedCounter value={data.adminStats?.totalScripts || 0} />
                  </Typography>
                  <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.8)', mb: 1, fontWeight: 500 }}>
                    Scripts
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#06b6d4', fontWeight: 600 }}>
                    Today: +<AnimatedCounter value={data.adminStats?.scriptsGeneratedToday || 0} />
                  </Typography>
                </Box>

                {/* Videos */}
                <Box sx={{ textAlign: 'center', flex: 1 }}>
                  <Box
                    sx={{
                      width: 64,
                      height: 64,
                      borderRadius: 3,
                      background: 'linear-gradient(135deg, #22c55e, #16a34a)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                      margin: '0 auto 16px auto',
                      boxShadow: '0 8px 32px rgba(34, 197, 94, 0.3)',
                    }}
                  >
                    <VideoIcon sx={{ fontSize: 32 }} />
                  </Box>
                  <Typography variant="h3" sx={{ color: 'white', fontWeight: 800, mb: 1 }}>
                    <AnimatedCounter value={data.adminStats?.totalVideos || 0} />
                  </Typography>
                  <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.8)', mb: 1, fontWeight: 500 }}>
                    Videos
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#22c55e', fontWeight: 600 }}>
                    Today: +<AnimatedCounter value={data.adminStats?.videosCreatedToday || 0} />
                  </Typography>
                </Box>
              </Box>
            </ModernCard>
          </Box>

          {/* ROW 2: SYSTEM HEALTH | TODAY'S ACTIVITY */}
          <Box sx={{ display: 'flex', gap: 3, mb: 4 }}>
            {/* System Health */}
            <Box sx={{ flex: 1 }}>
              <ModernCard
                title="System Health"
                icon={<SystemIcon />}
                action={
                  <Chip
                    label="All Systems"
                    size="small"
                    sx={{
                      backgroundColor: 'rgba(34, 197, 94, 0.2)',
                      color: '#22c55e',
                      border: '1px solid rgba(34, 197, 94, 0.3)',
                    }}
                  />
                }
              >
                <Stack spacing={3}>
                  <StatusIndicator
                    status={data.f5ttsStatus?.status || 'Unknown'}
                    label="F5-TTS Service"
                    description="Text-to-speech engine"
                  />
                  <StatusIndicator
                    status={data.ffmpegStatus?.status || 'Unknown'}
                    label="FFmpeg Engine"
                    description="Video processing pipeline"
                  />
                  <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <AccessTimeIcon sx={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: 16 }} />
                      <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                        Last health check: {formatTimeAgo(data.systemStatus?.timestamp || '')}
                      </Typography>
                    </Stack>
                  </Box>
                </Stack>
              </ModernCard>
            </Box>

            {/* Processing Queue */}
            <Box sx={{ flex: 1 }}>
              <ModernCard
                title="Processing Queue"
                icon={<VideoIcon />}
                action={
                  <Badge
                    badgeContent={data.queueStatus?.queue_size || 0}
                    color="warning"
                    max={99}
                  >
                    <Box
                      sx={{
                        width: 24,
                        height: 24,
                        borderRadius: '50%',
                        backgroundColor: data.queueStatus?.current_job_id ? '#22c55e' : '#64748b',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      {data.queueStatus?.current_job_id ? (
                        <PlayArrowIcon sx={{ fontSize: 14, color: 'white' }} />
                      ) : (
                        <PauseIcon sx={{ fontSize: 14, color: 'white' }} />
                      )}
                    </Box>
                  </Badge>
                }
              >
                <Stack spacing={3}>
                  <Box>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                      Queue Status
                    </Typography>
                    <Stack direction="row" alignItems="center" spacing={2}>
                      <Typography variant="h4" sx={{ color: 'white', fontWeight: 700 }}>
                        {data.queueStatus?.queue_size || 0}
                      </Typography>
                      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                        jobs pending
                      </Typography>
                    </Stack>
                  </Box>

                  <Box>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                      Today's Output
                    </Typography>
                    <Typography variant="h5" sx={{ color: '#22c55e', fontWeight: 600 }}>
                      <AnimatedCounter value={data.adminStats?.videosCreatedToday || 0} />
                    </Typography>
                  </Box>

                  <LinearProgress
                    variant="determinate"
                    value={data.queueStatus?.queue_size ? Math.min((data.queueStatus.queue_size / 10) * 100, 100) : 0}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                      '& .MuiLinearProgress-bar': {
                        background: 'linear-gradient(90deg, #f59e0b, #ef4444)',
                        borderRadius: 4,
                      },
                    }}
                  />
                </Stack>
              </ModernCard>
            </Box>
          </Box>

          {/* ROW 3: RECENT USERS & TOKEN ECONOMY */}
          <Box sx={{ mb: 4 }}>
            <ModernCard
              title="Recent Users & Token Economy"
              icon={<PeopleIcon />}
            >
              <Box sx={{ display: 'flex', gap: 4 }}>
                {/* Recent Users Section */}
                <Box sx={{ flex: 1 }}>
                  <Typography variant="h6" sx={{ color: 'white', fontWeight: 600, mb: 2 }}>
                    Recent Users
                  </Typography>
                  <Stack spacing={2}>
                    {data.recentUsers.slice(0, 3).map((user) => (
                      <Stack key={user.id} direction="row" alignItems="center" spacing={2}>
                        <Avatar
                          sx={{
                            width: 32,
                            height: 32,
                            background: `linear-gradient(135deg, #3b82f6, #1d4ed8)`,
                            fontSize: '0.75rem',
                            fontWeight: 600,
                          }}
                        >
                          {user.name.charAt(0).toUpperCase()}
                        </Avatar>
                        <Box sx={{ flex: 1 }}>
                          <Typography variant="body2" sx={{ color: 'white', fontWeight: 500 }}>
                            {user.name}
                          </Typography>
                          <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                            {formatTimeAgo(user.createdAt)}
                          </Typography>
                        </Box>
                        <Chip
                          label={`${user.tokens}`}
                          size="small"
                          sx={{
                            backgroundColor: 'rgba(245, 158, 11, 0.2)',
                            color: '#f59e0b',
                            border: '1px solid rgba(245, 158, 11, 0.3)',
                            fontWeight: 600,
                            fontSize: '0.7rem',
                          }}
                        />
                      </Stack>
                    ))}
                  </Stack>
                </Box>

                {/* Divider */}
                <Divider orientation="vertical" flexItem sx={{ borderColor: 'rgba(255, 255, 255, 0.1)' }} />

                {/* Token Economy Section */}
                <Box sx={{ flex: 1 }}>
                  <Typography variant="h6" sx={{ color: 'white', fontWeight: 600, mb: 2 }}>
                    Token Economy
                  </Typography>
                  <Stack spacing={2}>
                    <Box>
                      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 0.5 }}>
                        Total in Circulation
                      </Typography>
                      <Typography variant="h5" sx={{ color: '#f59e0b', fontWeight: 700 }}>
                        <AnimatedCounter 
                          value={data.adminStats?.totalTokens || 0}
                          formatter={(v) => v.toLocaleString()}
                        />
                      </Typography>
                    </Box>

                    <Box>
                      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 0.5 }}>
                        Average per User
                      </Typography>
                      <Typography variant="h6" sx={{ color: '#06b6d4', fontWeight: 600 }}>
                        <AnimatedCounter value={data.adminStats?.averageTokensPerUser || 0} />
                      </Typography>
                    </Box>

                    {data.adminStats?.topTokenUser && (
                      <Box 
                        sx={{ 
                          p: 1.5, 
                          background: 'rgba(245, 158, 11, 0.1)',
                          borderRadius: 2,
                          border: '1px solid rgba(245, 158, 11, 0.2)',
                        }}
                      >
                        <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                          👑 Top Holder
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', fontWeight: 600 }}>
                          {data.adminStats.topTokenUser.name}
                        </Typography>
                        <Typography variant="caption" sx={{ color: '#f59e0b', fontWeight: 600 }}>
                          {data.adminStats.topTokenUser.tokens.toLocaleString()} tokens
                        </Typography>
                      </Box>
                    )}
                  </Stack>
                </Box>
              </Box>
            </ModernCard>
          </Box>
        </Container>

        {/* Enhanced Snackbar */}
        <Snackbar
          open={snackbar.open}
          autoHideDuration={6000}
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert
            severity={snackbar.severity}
            onClose={() => setSnackbar({ ...snackbar, open: false })}
            sx={{
              background: 'rgba(30, 41, 59, 0.95)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              color: 'white',
              borderRadius: 2,
            }}
          >
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Box>
    </DashboardLayout>
  );
}; 