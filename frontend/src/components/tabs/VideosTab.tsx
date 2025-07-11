import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Paper,
  Fade,
  Card,
  CardContent,
  Chip,
  Skeleton,
  Alert,
  Button,
  Slide,
  Collapse,
} from '@mui/material';
import {
  VideoFile as VideoIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  Error as ErrorIcon,
  PlayArrow as PlayArrowIcon,
  PeopleAlt as PeopleIcon,
  Audiotrack as AudioIcon,
  Timeline as TimelineIcon,
  MusicNote as MusicIcon,
  Verified as VerifiedIcon,
  QueueMusic as QueueMusicIcon,
  Settings as SettingsIcon,
  Cancel as CancelIcon,
  Chat as ChatIcon,
  CalendarToday as CalendarIcon,
  Download as DownloadIcon,
  Edit as EditIcon,
} from '@mui/icons-material';
import { scriptAPI, type Script, type MyScriptsResponse, API_BASE_URL } from '../../services/api';
import { useAuth } from '../../hooks/useAuth';

// Dynamic Processing Message Component
interface DynamicProcessingMessageProps {
  currentStep: string;
  progress: number;
}

const DynamicProcessingMessage: React.FC<DynamicProcessingMessageProps> = ({ currentStep, progress }) => {
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);
  const [slideDirection, setSlideDirection] = useState<'left' | 'right' | 'up' | 'down'>('left');

  const encouragingMessages = [
    "Creating something amazing for you...",
    "Your video is coming to life!",
    "AI is working its magic...",
    "Almost there, stay tuned!",
    "Bringing characters to life...",
    "Crafting the perfect audio...",
    "Adding the finishing touches...",
    "Processing at lightning speed...",
    "Making it perfect for you...",
    "The show is about to begin!",
    "Quality is worth the wait...",
    "Precision work in progress...",
    "Almost ready to amaze you!",
    "Creating something spectacular...",
    "Polishing your masterpiece..."
  ];

  const getStepInfo = (step: string) => {
    switch (step) {
      case 'audio_validation':
        return { icon: <VerifiedIcon sx={{ fontSize: 14 }} />, label: 'Validating Audio Files', color: '#3b82f6' };
      case 'audio_generation':
        return { icon: <AudioIcon sx={{ fontSize: 14 }} />, label: 'Generating Character Voices', color: '#8b5cf6' };
      case 'timeline_creation':
        return { icon: <TimelineIcon sx={{ fontSize: 14 }} />, label: 'Creating Video Timeline', color: '#06b6d4' };
      case 'audio_concatenation':
        return { icon: <MusicIcon sx={{ fontSize: 14 }} />, label: 'Combining Audio Tracks', color: '#10b981' };
      case 'video_generation':
        return { icon: <VideoIcon sx={{ fontSize: 14 }} />, label: 'Generating Final Video', color: '#f59e0b' };
      case 'queued':
        return { icon: <QueueMusicIcon sx={{ fontSize: 14 }} />, label: 'Preparing Your Request', color: '#94a3b8' };
      default:
        return { icon: <SettingsIcon sx={{ fontSize: 14 }} />, label: 'Processing Your Video', color: '#f59e0b' };
    }
  };

  const directions: Array<'left' | 'right' | 'up' | 'down'> = ['left', 'right', 'up', 'down'];

  useEffect(() => {
    const interval = setInterval(() => {
      // Random slide direction
      const randomDirection = directions[Math.floor(Math.random() * directions.length)];
      setSlideDirection(randomDirection);
      
      // Cycle through messages
      setCurrentMessageIndex((prev) => (prev + 1) % encouragingMessages.length);
    }, 5000); // Change message every 3 seconds

    return () => clearInterval(interval);
  }, []);

  const stepInfo = getStepInfo(currentStep);

    return (
    <Box sx={{ mb: 2 }}>
      {/* Compact Process Step with Icon */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
        <Box 
          sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            width: 20,
            height: 20,
            borderRadius: '50%',
            background: `${stepInfo.color}20`,
            color: stepInfo.color,
            animation: 'pulse 2s infinite'
          }}
        >
          {stepInfo.icon}
        </Box>
        <Typography 
          variant="body2" 
          sx={{ 
            fontSize: '0.8rem',
            fontWeight: 600,
            color: stepInfo.color,
            flex: 1
          }}
        >
          {stepInfo.label}
        </Typography>
        <Typography 
          variant="caption" 
          sx={{ 
            fontSize: '0.7rem',
            color: 'text.secondary',
            fontWeight: 500
          }}
        >
          {Math.round(progress)}%
        </Typography>
      </Box>
      
      {/* Subtle Progress Bar */}
      <Box sx={{ position: 'relative', mb: 1 }}>
        <Box 
          sx={{
            height: 3,
            borderRadius: 1.5,
            backgroundColor: 'rgba(148, 163, 184, 0.15)',
            overflow: 'hidden',
            position: 'relative'
          }}
        >
          <Box
            sx={{
              height: '100%',
              width: `${progress}%`,
              background: `linear-gradient(90deg, ${stepInfo.color}80 0%, ${stepInfo.color} 100%)`,
              borderRadius: 1.5,
              position: 'relative',
              transition: 'width 0.3s ease-in-out',
              '&::after': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: `linear-gradient(90deg, transparent 0%, ${stepInfo.color}30 50%, transparent 100%)`,
                animation: 'shimmer 2s infinite'
              }
            }}
          />
        </Box>
      </Box>
      
      {/* Compact Encouraging Message */}
      <Box sx={{ height: 16, overflow: 'hidden', position: 'relative' }}>
        <Slide 
          direction={slideDirection} 
          in={true} 
          timeout={400}
          key={`${currentMessageIndex}-${slideDirection}`}
        >
          <Typography 
            variant="caption" 
            sx={{ 
              fontSize: '0.7rem',
              color: 'text.secondary',
              textAlign: 'center',
              display: 'block',
              fontStyle: 'italic',
              opacity: 0.8
            }}
          >
            {encouragingMessages[currentMessageIndex]}
          </Typography>
        </Slide>
      </Box>

      {/* Minimal CSS Animations */}
      <style>
        {`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
          }
          @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
          }
        `}
      </style>
    </Box>
  );
};

interface VideoCardProps {
  script: Script;
  autoExpand?: boolean;
}

const VideoCard: React.FC<VideoCardProps> = ({ script, autoExpand = false }) => {
  const [isExpanded, setIsExpanded] = useState(autoExpand);
  const [isPlaying, setIsPlaying] = useState(autoExpand);
  const cardRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  // Auto-scroll to card when auto-expanded
  useEffect(() => {
    if (autoExpand && cardRef.current) {
      setTimeout(() => {
        cardRef.current?.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'center' 
        });
      }, 100); // Small delay to ensure DOM is ready
    }
  }, [autoExpand]);

  const getStatusIcon = () => {
    if (script.finalVideoPath) {
      return <CheckCircleIcon sx={{ color: '#22c55e' }} />;
    } else if (script.videoJobStatus === 'in_progress') {
      return <ScheduleIcon sx={{ color: '#f59e0b' }} />;
    } else if (script.videoJobStatus === 'queued') {
      return <ScheduleIcon sx={{ color: '#94a3b8' }} />;
    } else if (script.videoJobStatus === 'failed') {
      return <ErrorIcon sx={{ color: '#ef4444' }} />;
    } else {
      return <ScheduleIcon sx={{ color: '#f59e0b' }} />;
    }
  };

  const getStatusColor = () => {
    if (script.finalVideoPath) return '#22c55e';
    if (script.videoJobStatus === 'in_progress') return '#f59e0b';
    if (script.videoJobStatus === 'queued') return '#94a3b8';
    if (script.videoJobStatus === 'failed') return '#ef4444';
    return '#f59e0b';
  };

  const getStatusText = () => {
    if (script.finalVideoPath) return 'Completed';
    if (script.videoJobStatus === 'in_progress') return `Processing (${Math.round(script.videoJobProgress || 0)}%)`;
    if (script.videoJobStatus === 'queued') return 'Queued';
    if (script.videoJobStatus === 'failed') return 'Failed';
    return 'Ready';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handlePlayVideo = () => {
    if (script.finalVideoPath) {
      setIsExpanded(true);
      setIsPlaying(true); // This will render the video element, but it won't autoplay
    }
  };

  const handleCancelVideo = () => {
    setIsExpanded(false);
    setIsPlaying(false);
  };

  const getVideoUrl = () => {
    if (script.finalVideoPath) {
      // Use the same pattern as images: API_BASE_URL + path
      const cleanPath = script.finalVideoPath.replace(/\\/g, '/');
      const relativePath = cleanPath.startsWith('apiData/') 
        ? cleanPath.replace('apiData/', '') 
        : cleanPath;
      const fullUrl = `${API_BASE_URL}/api/static/${relativePath}`;
      console.log('🎬 Video URL generated:', {
        originalPath: script.finalVideoPath,
        cleanPath,
        relativePath,
        fullUrl
      });
      return fullUrl;
    }
    return '';
  };

  const handleDownloadVideo = () => {
    if (script.finalVideoPath) {
      const videoUrl = getVideoUrl();
      const fileName = `Script_${script.id.slice(-6)}_${script.originalPrompt.slice(0, 30).replace(/[^a-zA-Z0-9]/g, '_')}.mp4`;
      
      // Create a temporary link element to trigger download
      const link = document.createElement('a');
      link.href = videoUrl;
      link.download = fileName;
      link.target = '_blank';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      console.log('📥 Download initiated:', fileName);
    }
  };

  const handleEditScript = () => {
    // Navigate to scripts page with script ID parameter for auto-expansion and editing
    navigate(`/scripts?edit=${script.id}`);
  };

  return (
    <Card
      ref={cardRef}
      elevation={0}
      sx={{
        borderRadius: 3,
        background: 'rgba(30, 41, 59, 0.6)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(148, 163, 184, 0.1)',
        height: 'fit-content', // Allow dynamic height
        alignSelf: 'start', // Prevent stretching in grid
        '&:hover': {
          border: '1px solid rgba(99, 102, 241, 0.3)',
        },
      }}
    >
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <VideoIcon sx={{ color: 'primary.main', fontSize: 20 }} />
            <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '1rem' }}>
              Script #{script.id.slice(-6)}
            </Typography>
          </Box>
          
          <Chip
            icon={getStatusIcon()}
            label={getStatusText()}
            size="small"
            sx={{
              backgroundColor: `${getStatusColor()}15`,
              color: getStatusColor(),
              fontWeight: 600,
              fontSize: '0.75rem',
            }}
          />
        </Box>

        <Typography variant="body2" sx={{ color: 'text.secondary', mb: 2 }}>
          {script.originalPrompt.length > 100 
            ? `${script.originalPrompt.substring(0, 100)}...`
            : script.originalPrompt
          }
        </Typography>

        <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
          <Chip
            size="small"
            icon={<PeopleIcon sx={{ fontSize: '12px !important' }} />}
            label={script.selectedCharacters.length}
            sx={{
              backgroundColor: 'rgba(99, 102, 241, 0.1)',
              color: 'primary.main',
              fontWeight: 600,
              fontSize: '0.7rem',
            }}
          />
          <Chip
            size="small"
            icon={<ChatIcon sx={{ fontSize: '12px !important' }} />}
            label={`${script.dialogue.length} Lines`}
            sx={{
              backgroundColor: 'rgba(34, 197, 94, 0.1)',
              color: '#22c55e',
              fontWeight: 600,
              fontSize: '0.7rem',
            }}
          />
          <Chip
            size="small"
            icon={<CalendarIcon sx={{ fontSize: '12px !important' }} />}
            label={`${formatDate(script.createdAt)}`}
            sx={{
              backgroundColor: 'rgba(148, 163, 184, 0.1)',
              color: 'text.secondary',
              fontWeight: 600,
              fontSize: '0.7rem',
            }}
          />
        </Box>

        {/* Progress bar for active jobs */}
        {script.videoJobStatus && (script.videoJobStatus === 'queued' || script.videoJobStatus === 'in_progress') && (
          <DynamicProcessingMessage
            currentStep={script.videoJobCurrentStep || 'processing'}
            progress={script.videoJobProgress || 0}
          />
        )}

        <Box sx={{ display: 'flex', gap: 1, justifyContent: 'space-between', alignItems: 'center' }}>
          {script.finalVideoPath && (
            <>
              <Button
                variant="outlined"
                size="small"
                startIcon={<EditIcon />}
                onClick={handleEditScript}
                sx={{
                  fontSize: '0.8rem',
                  py: 0.5,
                  px: 2,
                  borderRadius: 2,
                  fontWeight: 600,
                  borderColor: 'rgba(168, 85, 247, 0.5)',
                  color: '#a855f7',
                  '&:hover': {
                    backgroundColor: 'rgba(168, 85, 247, 0.1)',
                    borderColor: '#a855f7',
                    transform: 'translateY(-1px)',
                    boxShadow: '0 4px 12px rgba(168, 85, 247, 0.2)',
                  },
                }}
              >
                Edit
              </Button>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<DownloadIcon />}
                  onClick={handleDownloadVideo}
                  sx={{
                    fontSize: '0.8rem',
                    py: 0.5,
                    px: 2,
                    borderRadius: 2,
                    fontWeight: 600,
                    borderColor: 'rgba(99, 102, 241, 0.5)',
                    color: '#6366f1',
                    '&:hover': {
                      backgroundColor: 'rgba(99, 102, 241, 0.1)',
                      borderColor: '#6366f1',
                      transform: 'translateY(-1px)',
                      boxShadow: '0 4px 12px rgba(99, 102, 241, 0.2)',
                    },
                  }}
                >
                  Download
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={isExpanded ? <CancelIcon /> : <PlayArrowIcon />}
                  onClick={isExpanded ? handleCancelVideo : handlePlayVideo}
                  sx={{
                    fontSize: '0.8rem',
                    py: 0.5,
                    px: 2,
                    borderRadius: 2,
                    fontWeight: 600,
                    borderColor: isExpanded ? 'rgba(239, 68, 68, 0.5)' : 'rgba(34, 197, 94, 0.5)',
                    color: isExpanded ? '#ef4444' : '#22c55e',
                    '&:hover': {
                      backgroundColor: isExpanded ? 'rgba(239, 68, 68, 0.1)' : 'rgba(34, 197, 94, 0.1)',
                      borderColor: isExpanded ? '#ef4444' : '#22c55e',
                      transform: 'translateY(-1px)',
                      boxShadow: isExpanded ? '0 4px 12px rgba(239, 68, 68, 0.2)' : '0 4px 12px rgba(34, 197, 94, 0.2)',
                    },
                  }}
                >
                  {isExpanded ? 'Cancel' : 'Play Video'}
                </Button>
              </Box>
            </>
          )}
        </Box>

        {/* Expanded Video Player */}
        <Collapse in={isExpanded} timeout={500}>
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <PlayArrowIcon sx={{ color: 'primary.main', fontSize: 20 }} />
                <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>
                  Video Player
                </Typography>
              </Box>
            </Box>
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                background: 'linear-gradient(135deg, rgba(0, 0, 0, 0.95) 0%, rgba(30, 41, 59, 0.9) 100%)',
                borderRadius: 3,
                p: 3,
                minHeight: 450,
                border: '1px solid rgba(99, 102, 241, 0.2)',
                position: 'relative',
                overflow: 'hidden',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  background: `
                    radial-gradient(circle at 20% 80%, rgba(99, 102, 241, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.1) 0%, transparent 50%)
                  `,
                  opacity: 0.5,
                  pointerEvents: 'none',
                },
              }}
            >
              {isPlaying && script.finalVideoPath ? (
                <Box
                  component="video"
                  controls
                  preload="metadata"
                  sx={{
                    maxWidth: '100%',
                    maxHeight: '70vh',
                    height: 'auto',
                    borderRadius: 2,
                    // Optimized for vertical videos (portrait orientation)
                    aspectRatio: '9/16',
                    objectFit: 'contain',
                    background: '#000',
                    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.5)',
                    position: 'relative',
                    zIndex: 1,
                  }}
                  src={getVideoUrl()}
                  onError={(e) => {
                    console.error('Video failed to load:', e);
                  }}
                  onEnded={() => {
                    console.log('Video playback ended');
                  }}
                />
              ) : (
                <Box
                  sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: 2,
                    color: 'text.secondary',
                    position: 'relative',
                    zIndex: 1,
                  }}
                >
                  <VideoIcon sx={{ fontSize: 64, opacity: 0.5 }} />
                  <Typography variant="body1" sx={{ textAlign: 'center' }}>
                    Preparing video player...
                  </Typography>
                </Box>
              )}
            </Box>
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  );
};

export const VideosTab: React.FC = () => {
  const [scripts, setScripts] = useState<Script[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchParams, setSearchParams] = useSearchParams();
  const targetScriptId = searchParams.get('script');
  const { updateUserTokens } = useAuth();

  // Fetch scripts with embedded video job information
  const fetchScripts = async (showLoader: boolean = true) => {
    try {
      if (showLoader) {
        setLoading(true);
      }
      const response: MyScriptsResponse = await scriptAPI.getMyScripts();
      setScripts(response.scripts);
      
      // Update user tokens if they changed
      updateUserTokens(response.userTokens);
      
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load scripts';
      setError(errorMessage);
    } finally {
      if (showLoader) {
        setLoading(false);
      }
    }
  };

  // Auto-refresh every 3 seconds for scripts with active video jobs
  useEffect(() => {
    fetchScripts();

    const interval = setInterval(() => {
      // Only refresh if there are active jobs
      const hasActiveJobs = scripts.some(script => 
        script.videoJobStatus === 'queued' || script.videoJobStatus === 'in_progress'
      );
      
      if (hasActiveJobs) {
        fetchScripts(false); // Silent refresh without loader
      }
    }, 5000); // Refresh every 3 seconds

    return () => clearInterval(interval);
  }, [scripts.length]); // Only depend on scripts.length to avoid infinite loops

  // Clear URL parameter after auto-expansion is handled
  useEffect(() => {
    if (targetScriptId && scripts.length > 0) {
      // Clear the script parameter from URL after a delay to allow auto-expansion
      setTimeout(() => {
        setSearchParams({});
      }, 1000);
    }
  }, [targetScriptId, scripts.length, setSearchParams]);



  if (loading) {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
          <Box sx={{ mb: 4 }}>
            <Typography variant="h3" sx={{ fontWeight: 800, mb: 2 }}>
              Videos
            </Typography>
            <Typography variant="h6" sx={{ color: 'text.secondary', mb: 4 }}>
              Your video library and projects
            </Typography>
          </Box>

        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))', gap: 3 }}>
          {Array.from({ length: 3 }).map((_, idx) => (
            <Card
              key={idx}
              elevation={0}
              sx={{
                borderRadius: 3,
                background: 'rgba(30, 41, 59, 0.6)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(148, 163, 184, 0.1)',
              }}
            >
              <CardContent sx={{ p: 3 }}>
                {/* Header with Video Title and Status */}
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Skeleton variant="circular" width={20} height={20} />
                    <Skeleton variant="text" width={120} height={24} />
                  </Box>
                  <Skeleton variant="rounded" width={80} height={24} sx={{ borderRadius: 2 }} />
                </Box>

                {/* Prompt Text */}
                <Box sx={{ mb: 2 }}>
                  <Skeleton variant="text" width="100%" height={20} />
                  <Skeleton variant="text" width="80%" height={20} />
                </Box>

                {/* Stats Chips */}
                <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                  <Skeleton variant="rounded" width={50} height={24} sx={{ borderRadius: 2 }} />
                  <Skeleton variant="rounded" width={70} height={24} sx={{ borderRadius: 2 }} />
                  <Skeleton variant="rounded" width={100} height={24} sx={{ borderRadius: 2 }} />
                </Box>

                {/* Progress Bar Area (for in-progress videos) */}
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Skeleton variant="circular" width={20} height={20} />
                    <Skeleton variant="text" width="60%" height={16} />
                    <Skeleton variant="text" width={30} height={16} />
                  </Box>
                  <Skeleton variant="rounded" width="100%" height={3} sx={{ borderRadius: 1.5, mb: 1 }} />
                  <Skeleton variant="text" width="50%" height={14} />
                </Box>

                {/* Action Buttons */}
                <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                  <Skeleton variant="rounded" width={110} height={32} sx={{ borderRadius: 2 }} />
                </Box>
              </CardContent>
            </Card>
          ))}
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert 
          severity="error" 
          sx={{ mb: 4 }}
          action={
            <Button color="inherit" size="small" onClick={() => fetchScripts()}>
              Retry
            </Button>
          }
        >
          {error}
        </Alert>
      </Container>
    );
  }

  // Filter scripts to only show completed videos or videos in progress
  const filteredScripts = scripts.filter(script => 
    script.finalVideoPath || 
    script.videoJobStatus === 'in_progress' || 
    script.videoJobStatus === 'queued' ||
    script.videoJobStatus === 'failed'
  ).sort((a, b) => {
    // Sort by last updated first, if not then last created first
    const aUpdated = new Date(a.updatedAt || a.createdAt).getTime();
    const bUpdated = new Date(b.updatedAt || b.createdAt).getTime();
    return bUpdated - aUpdated;
  });

  if (filteredScripts.length === 0) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Fade in timeout={800}>
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 4 }}>
              <Box>
                <Typography variant="h3" sx={{ fontWeight: 800, mb: 1 }}>
                  Videos
                </Typography>
                <Typography variant="h6" sx={{ color: 'text.secondary' }}>
                  Your video library and projects
                </Typography>
              </Box>
            </Box>

          <Paper
            elevation={0}
            sx={{
              p: 8,
              borderRadius: 3,
              textAlign: 'center',
              background: 'rgba(30, 41, 59, 0.8)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(148, 163, 184, 0.1)',
            }}
          >
            <Box
              sx={{
                width: 120,
                height: 120,
                borderRadius: '50%',
                  background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mx: 'auto',
                mb: 3,
                opacity: 0.8,
              }}
            >
              <VideoIcon sx={{ fontSize: 60, color: 'white' }} />
            </Box>
            
            <Typography variant="h4" sx={{ fontWeight: 700, mb: 2 }}>
              No Videos to Display
            </Typography>
            
            <Typography variant="h6" sx={{ color: 'text.secondary', mb: 4, maxWidth: 500, mx: 'auto' }}>
                Only completed videos and videos in progress are shown here. Generate videos from your scripts to see them appear with real-time updates.
              </Typography>
            </Paper>
          </Box>
        </Fade>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Fade in timeout={800}>
        <Box>
          <Box sx={{ mb: 4 }}>
            <Typography variant="h3" sx={{ fontWeight: 800, mb: 1 }}>
              Videos
            </Typography>
            <Typography variant="h6" sx={{ color: 'text.secondary' }}>
              {filteredScripts.length} video{filteredScripts.length !== 1 ? 's' : ''}
            </Typography>
          </Box>

          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))', 
            gap: 3,
            alignItems: 'start' // Prevent cards from stretching to match tallest card
          }}>
            {filteredScripts.map((script) => (
              <VideoCard 
                key={script.id}
                script={script}
                autoExpand={script.id === targetScriptId}
              />
            ))}
          </Box>
        </Box>
      </Fade>
    </Container>
  );
}; 