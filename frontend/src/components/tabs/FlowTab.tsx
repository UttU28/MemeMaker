import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Fade,
  Button,
  Stack,
  Card,
  CardContent,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  Login as LoginIcon,
  VpnKey as VpnKeyIcon,
  RecordVoiceOver as VoiceCloneIcon,
  AutoAwesome as AIScriptIcon,
  Timeline as TimelineIcon,
  Storage as DatabaseIcon,
  MonetizationOn as TokenIcon,
  AutoAwesome as MagicIcon,
  Queue as ProcessingIcon,
  CheckCircle as CheckIcon,
  PlayArrow as PlayIcon,
  PersonAdd as PersonAddIcon,
  VideoCall as VideoCallIcon,
  Psychology as BrainIcon,
  Speaker as SpeakerIcon,
} from '@mui/icons-material';

interface FlowNodeProps {
  title: string;
  icon: React.ReactNode;
  color: string;
  isActive: boolean;
  isCompleted: boolean;
  position: { x: number; y: number };
  onClick: () => void;
  size?: 'small' | 'medium' | 'large';
}

const FlowNode: React.FC<FlowNodeProps> = ({
  title,
  icon,
  color,
  isActive,
  isCompleted,
  position,
  onClick,
  size = 'medium',
}) => {
  const sizeMap = {
    small: { width: 60, height: 60, iconSize: 20 },
    medium: { width: 80, height: 80, iconSize: 24 },
    large: { width: 100, height: 100, iconSize: 28 },
  };

  const nodeSize = sizeMap[size];

  return (
    <Box
      sx={{
        position: 'absolute',
        left: position.x,
        top: position.y,
        transform: 'translate(-50%, -50%)',
        zIndex: isActive ? 10 : 5,
        transition: 'all 0.3s ease',
      }}
    >
      <Box
        onClick={onClick}
        sx={{
          width: nodeSize.width,
          height: nodeSize.height,
          borderRadius: '50%',
          background: isActive
            ? `linear-gradient(135deg, ${color}, ${color}dd)`
            : `linear-gradient(135deg, ${color}80, ${color}60)`,
          border: isActive ? `4px solid ${color}` : `2px solid ${color}60`,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
          boxShadow: isActive
            ? `0 12px 40px ${color}80, 0 0 20px ${color}40`
            : `0 6px 20px ${color}40`,
          animation: isActive ? 'pulse 2s infinite' : 'none',
          '&:hover': {
            transform: 'scale(1.1) translateY(-4px)',
            boxShadow: `0 16px 50px ${color}90, 0 0 30px ${color}60`,
            border: `4px solid ${color}`,
            background: `linear-gradient(135deg, ${color}, ${color}ee)`,
          },
          '@keyframes pulse': {
            '0%': {
              boxShadow: `0 12px 40px ${color}80, 0 0 20px ${color}40`,
            },
            '50%': {
              boxShadow: `0 16px 50px ${color}90, 0 0 30px ${color}60`,
            },
            '100%': {
              boxShadow: `0 12px 40px ${color}80, 0 0 20px ${color}40`,
            },
          },
        }}
      >
        <Box
          sx={{
            color: 'white',
            fontSize: nodeSize.iconSize,
            mb: 0.2,
          }}
        >
          {icon}
        </Box>
        <Typography
          variant="caption"
          sx={{
            color: 'white',
            fontWeight: 400,
            fontSize: size === 'large' ? '0.85rem' : '0.65rem',
            textAlign: 'center',
            lineHeight: 1.1,
          }}
        >
          {title}
        </Typography>
        {isCompleted && (
          <CheckIcon
            sx={{
              position: 'absolute',
              top: -8,
              right: -8,
              color: '#22c55e',
              backgroundColor: 'white',
              borderRadius: '50%',
              fontSize: 20,
            }}
          />
        )}
      </Box>
    </Box>
  );
};

interface FlowConnectionProps {
  from: { x: number; y: number };
  to: { x: number; y: number };
  isActive: boolean;
  color: string;
  animated?: boolean;
}

const FlowConnection: React.FC<FlowConnectionProps> = ({
  from,
  to,
  isActive,
  color,
  animated = false,
}) => {
  const length = Math.sqrt(Math.pow(to.x - from.x, 2) + Math.pow(to.y - from.y, 2));
  const angle = Math.atan2(to.y - from.y, to.x - from.x) * (180 / Math.PI);

  return (
    <Box
      sx={{
        position: 'absolute',
        left: from.x,
        top: from.y,
        width: length,
        height: isActive ? 6 : 3, // Made thicker for better visibility
        background: isActive
          ? `linear-gradient(90deg, ${color}, ${color}ee, ${color})`
          : `linear-gradient(90deg, ${color}40, ${color}20)`, // More visible inactive state
        transformOrigin: '0 50%',
        transform: `rotate(${angle}deg)`,
        transition: 'all 0.4s ease',
        zIndex: isActive ? 3 : 1,
        borderRadius: 3,
        boxShadow: isActive ? `0 0 15px ${color}80, 0 0 30px ${color}40` : `0 0 5px ${color}30`, // Glow even when inactive
        '&::before': isActive
          ? {
              content: '""',
              position: 'absolute',
              top: -2,
              left: -2,
              width: 'calc(100% + 4px)',
              height: 'calc(100% + 4px)',
              background: `linear-gradient(90deg, transparent, ${color}60, transparent)`,
              borderRadius: 3,
              animation: 'glow 2s infinite alternate',
            }
          : {},
        '&::after': animated
          ? {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              background: `linear-gradient(90deg, transparent, ${color}, ${color}ee, transparent)`,
              borderRadius: 3,
              animation: 'flow 1.2s infinite',
            }
          : {},
        '@keyframes flow': {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
        '@keyframes glow': {
          '0%': { opacity: 0.6 },
          '100%': { opacity: 1 },
        },
      }}
    />
  );
};

export const FlowTab: React.FC = () => {
  const [activeNode, setActiveNode] = useState(0);
  const [completedNodes, setCompletedNodes] = useState<number[]>([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeExternalService, setActiveExternalService] = useState<number | null>(null);
  const [showExternalAPIs, setShowExternalAPIs] = useState(false);

  // Define flow nodes with technical process names
  const flowNodes = [
    // Step 1: User Entry
    {
      id: 'user',
      title: 'User Login\n& Auth Portal',
      icon: <LoginIcon />,
      color: '#3b82f6',
      position: { x: 400, y: 100 },
      size: 'large' as const,
    },
    // Step 2: Authentication
    {
      id: 'auth',
      title: 'JWT Token\nValidation',
      icon: <VpnKeyIcon />,
      color: '#3b82f6',
      position: { x: 400, y: 220 },
      size: 'large' as const,
    },
    // Step 3: Character Creation (branched)
    {
      id: 'character',
      title: 'Character\nCreation API',
      icon: <PersonAddIcon />,
      color: '#8b5cf6',
      position: { x: 250, y: 340 },
      size: 'large' as const,
    },
    // Step 4: Script Generation (branched)
    {
      id: 'script',
      title: 'OpenAI GPT\nScript Generation',
      icon: <BrainIcon />,
      color: '#06b6d4',
      position: { x: 550, y: 340 },
      size: 'large' as const,
    },
    // Step 5: Audio Generation (center merge)
    {
      id: 'audio',
      title: 'F5-TTS Voice\nCloning Engine',
      icon: <VoiceCloneIcon />,
      color: '#10b981',
      position: { x: 400, y: 460 },
      size: 'large' as const,
    },
    // Step 6: Timeline Creation
    {
      id: 'timeline',
      title: 'Video Timeline\nCreation',
      icon: <TimelineIcon />,
      color: '#f59e0b',
      position: { x: 400, y: 580 },
      size: 'large' as const,
    },
    // Step 7: Video Processing
    {
      id: 'video',
      title: 'FFmpeg Video\nComposition',
      icon: <VideoCallIcon />,
      color: '#ef4444',
      position: { x: 400, y: 700 },
      size: 'large' as const,
    },
    // Token System (side process)
    {
      id: 'tokens',
      title: 'Token Payment\nSystem',
      icon: <TokenIcon />,
      color: '#ec4899',
      position: { x: 650, y: 700 },
      size: 'medium' as const,
    },
  ];

  // Define connections for clean flow without admin dashboard
  const connections = [
    { from: 0, to: 1, color: '#3b82f6' }, // User -> Auth
    { from: 1, to: 2, color: '#3b82f6' }, // Auth -> Character (branch)
    { from: 1, to: 3, color: '#3b82f6' }, // Auth -> Script (branch)
    { from: 2, to: 4, color: '#8b5cf6' }, // Character -> Audio (merge)
    { from: 3, to: 4, color: '#06b6d4' }, // Script -> Audio (merge)
    { from: 4, to: 5, color: '#10b981' }, // Audio -> Timeline
    { from: 5, to: 6, color: '#f59e0b' }, // Timeline -> Video
    { from: 6, to: 7, color: '#ef4444' }, // Video -> Token System
  ];

  const handleNodeClick = (index: number) => {
    setActiveNode(index);
    setActiveExternalService(null);
    setShowExternalAPIs(false);
  };

  const handleExternalServiceClick = (serviceIndex: number) => {
    setActiveExternalService(serviceIndex);
    setActiveNode(-1); // Reset active node
    setShowExternalAPIs(false);
  };

  const handleExternalAPIsClick = () => {
    setShowExternalAPIs(true);
    setActiveExternalService(null);
    setActiveNode(-1);
  };

  const playFlow = () => {
    setIsPlaying(true);
    setCompletedNodes([]);
    setActiveNode(0);

    // Enhanced flow progression with dynamic timing
    const flowTimings = [500, 1200, 1800, 2400, 3200, 4000, 4800, 5400]; // Custom timing for each step

    flowNodes.forEach((_, index) => {
      setTimeout(() => {
        setActiveNode(index);
        
        // Add completion with a slight delay for better visual effect
        setTimeout(() => {
          setCompletedNodes(prev => [...prev, index]);
        }, 300);
        
        if (index === flowNodes.length - 1) {
          setTimeout(() => {
            setIsPlaying(false);
            // Celebration effect - briefly highlight all nodes
            setTimeout(() => {
              setCompletedNodes([]);
              setActiveNode(0);
            }, 2000);
          }, 1000);
        }
      }, flowTimings[index] || index * 1500);
    });
  };

  // Get description for each node with actual technical details
  const getNodeDescription = (nodeIndex: number) => {
    const descriptions = [
      "User authentication and login portal. Secure entry point to the MemeVoiceClone-inator platform. Creates JWT tokens for session management.",
      "JWT token validation and session management. Verifies user identity and permissions for accessing protected resources.",
      "Character Creation Process:\n• Input: displayName, audioFile (WAV/MP3/M4A/FLAC/OGG, max 50MB), imageFiles (PNG/JPG/WEBP, max 10 images)\n• Processing: Audio validation, image trimming/transparency removal, file storage\n• Config: speed, nfeSteps, crossFadeDuration, removeSilences\n• Output: character_id stored in Firebase with ownership tracking",
      "AI Script Generation Process:\n• Input: selectedCharacters (2-5 character IDs), prompt (topic/theme, 10-2000 chars)\n• Processing: OpenAI GPT-3.5-turbo API call with system prompt for political satire\n• Parsing: Character: dialogue format extraction\n• Output: script_id with dialogue array [{speaker, text, audioFile: ''}] saved to Firebase",
      "F5-TTS Voice Cloning Process:\n• Input: script_id, dialogue lines, character audio samples + configs\n• Processing: For each dialogue line, F5-TTS generates speech using character's voice sample\n• Sequential Processing: Exclusive F5-TTS access, generates audio files\n• Output: Updates dialogue array with generated audioFile paths (scriptId_lineIndex_speaker.wav)",
      "Video Timeline Creation Process:\n• Input: script data with audio files, user profiles with character images\n• Processing: Audio duration analysis, random character image selection, subtitle segmentation\n• Timeline Generation: Creates segments with startTime, endTime, audioFile, imageFile, subtitleSegments\n• Output: Timeline array with total duration for video composition",
      "FFmpeg Video Generation Process:\n• Input: Timeline, background video, combined audio, font path\n• Audio Concatenation: Combines all dialogue audio files into single WAV\n• Video Composition: 1080x1920, alternating left/right character images, subtitle overlay\n• Processing: CUDA acceleration, H264 encoding, AAC audio\n• Output: Final MP4 video file with file size tracking",
      "Token Payment System:\n• Input: User token balance check (requires 1 token per video)\n• Processing: Token deduction on video generation, balance updates\n• Management: User credit system, payment tracking\n• Output: Updated user token balance in Firebase",
    ];
    return descriptions[nodeIndex] || "System component in the video generation pipeline.";
  };

  // Get external service description - simplified based on actual backend usage
  const getExternalServiceDescription = (serviceIndex: number) => {
    const descriptions = [
      "Firebase Firestore Database:\n\n• User authentication and profile management with JWT tokens\n• Stores characters, scripts, and video metadata in real-time\n• Handles token balance tracking and payment processing",
      
      "OpenAI GPT-3.5-Turbo API:\n\n• Generates political satire dialogue scripts from user prompts\n• Uses custom system prompts for character-based conversations\n• Outputs structured dialogue with speaker assignments",
      
      "F5-TTS Voice Cloning Engine:\n\n• Clones voices from uploaded audio samples (5-30 seconds)\n• Generates speech for each dialogue line using character voices\n• Sequential processing with configurable voice settings"
    ];
    return descriptions[serviceIndex] || "External service information";
  };

  // Get external APIs overview description
  const getExternalAPIsDescription = () => {
    return "External Services Integration:\n\n• Firebase: User auth, data storage, and real-time sync\n• OpenAI GPT-3.5: AI script generation for political satire\n• F5-TTS: Voice cloning and speech synthesis";
  };

  // External services used in the backend pipeline
  const externalServices = [
    {
      title: 'Firebase\nFirestore DB',
      icon: <DatabaseIcon />,
      color: '#ff6b35',
      position: { x: 120, y: 220 },
    },
    {
      title: 'OpenAI\nGPT-3.5-Turbo',
      icon: <AIScriptIcon />,
      color: '#00d4aa',
      position: { x: 120, y: 340 },
    },
    {
      title: 'F5-TTS\nVoice Engine',
      icon: <SpeakerIcon />,
      color: '#4338ca',
      position: { x: 120, y: 460 },
    },
  ];

  return (
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
          <Box sx={{ mb: 4 }}>
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
                  Interactive System Flow
                </Typography>
                <Typography
                  variant="h6"
                  sx={{ color: 'rgba(255, 255, 255, 0.7)', fontWeight: 400 }}
                >
                  Visual diagram of the complete video generation pipeline
                </Typography>
              </Box>
              
              <Button
                variant="contained"
                startIcon={isPlaying ? <ProcessingIcon /> : <PlayIcon />}
                onClick={playFlow}
                disabled={isPlaying}
                sx={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  px: 3,
                  py: 1.5,
                  borderRadius: 2,
                  textTransform: 'none',
                  fontWeight: 600,
                  boxShadow: '0 4px 20px rgba(102, 126, 234, 0.3)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%)',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 8px 30px rgba(102, 126, 234, 0.4)',
                  },
                  '&:disabled': {
                    background: 'rgba(102, 126, 234, 0.3)',
                  },
                }}
              >
                {isPlaying ? 'Playing Flow...' : 'Animate Flow'}
              </Button>
            </Stack>

            {/* Progress Indicator */}
            {isPlaying && (
              <Box sx={{ mb: 3 }}>
                <LinearProgress
                  variant="determinate"
                  value={(completedNodes.length / flowNodes.length) * 100}
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      background: 'linear-gradient(90deg, #667eea, #764ba2)',
                      borderRadius: 4,
                    },
                  }}
                />
                <Typography
                  variant="body2"
                  sx={{ color: 'rgba(255, 255, 255, 0.7)', mt: 1, textAlign: 'center' }}
                >
                  Step {completedNodes.length} of {flowNodes.length}: {flowNodes[activeNode]?.title.replace('\n', ' ')}
                </Typography>
              </Box>
            )}
          </Box>
        </Fade>

        {/* Flow Diagram */}
        <Card
          sx={{
            background: 'rgba(255, 255, 255, 0.02)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: 3,
            overflow: 'visible',
          }}
        >
          <CardContent sx={{ p: 0 }}>
            <Box
              sx={{
                position: 'relative',
                height: 850, // Optimized height for smaller nodes
                width: '100%',
                overflow: 'hidden',
                background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.8) 100%)',
              }}
            >
              {/* Animated Background */}
              <Box
                sx={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  backgroundImage: `
                    linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)
                  `,
                  backgroundSize: '40px 40px',
                  opacity: 0.3,
                  animation: 'gridMove 20s linear infinite',
                  '@keyframes gridMove': {
                    '0%': { transform: 'translate(0, 0)' },
                    '100%': { transform: 'translate(40px, 40px)' },
                  },
                }}
              />

              {/* Floating Particles - positioned around edges to avoid interference */}
              {[...Array(8)].map((_, index) => (
                <Box
                  key={index}
                  sx={{
                    position: 'absolute',
                    width: 4,
                    height: 4,
                    borderRadius: '50%',
                    background: `linear-gradient(45deg, ${flowNodes[index % flowNodes.length]?.color}, transparent)`,
                    left: index < 4 ? `${5 + (index * 3)}%` : `${85 + ((index - 4) * 3)}%`,
                    top: `${10 + (index * 12)}%`,
                    animation: `float${index} ${10 + index}s ease-in-out infinite`,
                    '@keyframes float0': {
                      '0%, 100%': { transform: 'translateY(0px) rotate(0deg)', opacity: 0.6 },
                      '50%': { transform: 'translateY(-30px) rotate(180deg)', opacity: 1 },
                    },
                    '@keyframes float1': {
                      '0%, 100%': { transform: 'translateY(0px) rotate(0deg)', opacity: 0.4 },
                      '50%': { transform: 'translateY(-25px) rotate(90deg)', opacity: 0.8 },
                    },
                    '@keyframes float2': {
                      '0%, 100%': { transform: 'translateY(0px) rotate(0deg)', opacity: 0.5 },
                      '50%': { transform: 'translateY(-35px) rotate(270deg)', opacity: 0.9 },
                    },
                    '@keyframes float3': {
                      '0%, 100%': { transform: 'translateY(0px) rotate(0deg)', opacity: 0.3 },
                      '50%': { transform: 'translateY(-28px) rotate(45deg)', opacity: 0.7 },
                    },
                    '@keyframes float4': {
                      '0%, 100%': { transform: 'translateY(0px) rotate(0deg)', opacity: 0.6 },
                      '50%': { transform: 'translateY(-32px) rotate(135deg)', opacity: 1 },
                    },
                    '@keyframes float5': {
                      '0%, 100%': { transform: 'translateY(0px) rotate(0deg)', opacity: 0.4 },
                      '50%': { transform: 'translateY(-26px) rotate(225deg)', opacity: 0.8 },
                    },
                    '@keyframes float6': {
                      '0%, 100%': { transform: 'translateY(0px) rotate(0deg)', opacity: 0.5 },
                      '50%': { transform: 'translateY(-34px) rotate(315deg)', opacity: 0.9 },
                    },
                    '@keyframes float7': {
                      '0%, 100%': { transform: 'translateY(0px) rotate(0deg)', opacity: 0.7 },
                      '50%': { transform: 'translateY(-29px) rotate(180deg)', opacity: 1 },
                    },
                  }}
                />
              ))}

              {/* Enhanced Connections with thicker, more visible lines */}
              {connections.map((connection, index) => (
                <FlowConnection
                  key={index}
                  from={flowNodes[connection.from].position}
                  to={flowNodes[connection.to].position}
                  isActive={
                    completedNodes.includes(connection.from) && 
                    (activeNode === connection.to || completedNodes.includes(connection.to))
                  }
                  color={connection.color}
                  animated={isPlaying && activeNode === connection.to}
                />
              ))}

              {/* External Services (Background) - positioned further away */}
              {externalServices.map((service, index) => (
                <FlowNode
                  key={`external-${index}`}
                  title={service.title}
                  icon={service.icon}
                  color={service.color}
                  isActive={activeExternalService === index}
                  isCompleted={false}
                  position={service.position}
                  onClick={() => handleExternalServiceClick(index)}
                  size="small"
                />
              ))}

              {/* Main Flow Nodes */}
              {flowNodes.map((node, index) => (
                <FlowNode
                  key={node.id}
                  title={node.title}
                  icon={node.icon}
                  color={node.color}
                  isActive={activeNode === index}
                  isCompleted={completedNodes.includes(index)}
                  position={node.position}
                  onClick={() => handleNodeClick(index)}
                  size={node.size}
                />
              ))}



                            {/* Enhanced Technical Info Panel */}
              {(activeNode !== null || activeExternalService !== null || showExternalAPIs) && (
                <Box
                  sx={{
                    position: 'absolute',
                    top: 40,
                    right: 40,
                    background: `linear-gradient(135deg, ${(activeExternalService !== null || showExternalAPIs) ? '#667eea15' : flowNodes[activeNode]?.color + '15'}, ${(activeExternalService !== null || showExternalAPIs) ? '#667eea08' : flowNodes[activeNode]?.color + '08'})`,
                    backdropFilter: 'blur(20px)',
                    borderRadius: 4,
                    p: 4,
                    border: `2px solid ${(activeExternalService !== null || showExternalAPIs) ? '#667eea50' : flowNodes[activeNode]?.color + '50'}`,
                    width: 550,
                    maxHeight: '75vh',
                    overflowY: 'auto',
                    animation: 'slideIn 0.3s ease-out',
                    boxShadow: `0 8px 32px ${(activeExternalService !== null || showExternalAPIs) ? '#667eea30' : flowNodes[activeNode]?.color + '30'}`,
                    '@keyframes slideIn': {
                      '0%': { transform: 'translateX(100%)', opacity: 0 },
                      '100%': { transform: 'translateX(0)', opacity: 1 },
                    },
                    '&::-webkit-scrollbar': {
                      width: '8px',
                    },
                    '&::-webkit-scrollbar-track': {
                      background: 'rgba(255, 255, 255, 0.05)',
                      borderRadius: '4px',
                    },
                    '&::-webkit-scrollbar-thumb': {
                      background: `${(activeExternalService !== null || showExternalAPIs) ? '#667eea60' : flowNodes[activeNode]?.color + '60'}`,
                      borderRadius: '4px',
                      '&:hover': {
                        background: `${(activeExternalService !== null || showExternalAPIs) ? '#667eea80' : flowNodes[activeNode]?.color + '80'}`,
                      },
                    },
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                    <Box
                      sx={{
                        color: (activeExternalService !== null || showExternalAPIs) ? '#667eea' : flowNodes[activeNode]?.color,
                        fontSize: 32,
                        p: 1,
                        borderRadius: 2,
                        background: `${(activeExternalService !== null || showExternalAPIs) ? '#667eea' : flowNodes[activeNode]?.color}20`,
                      }}
                    >
                      {showExternalAPIs ? <DatabaseIcon /> : (activeExternalService !== null ? externalServices[activeExternalService]?.icon : flowNodes[activeNode]?.icon)}
                    </Box>
                    <Box>
                      <Typography variant="h6" sx={{ color: 'white', fontWeight: 500, lineHeight: 1.2 }}>
                        {showExternalAPIs ? 'External APIs Integration' : (activeExternalService !== null ? externalServices[activeExternalService]?.title.replace('\n', ' ') : flowNodes[activeNode]?.title.replace('\n', ' '))}
                      </Typography>
                      <Chip
                        label={showExternalAPIs ? 'Service Integration' : (activeExternalService !== null ? 'External Service' : `Step ${activeNode + 1} of ${flowNodes.length}`)}
                        size="small"
                        sx={{
                          backgroundColor: `${(activeExternalService !== null || showExternalAPIs) ? '#667eea' : flowNodes[activeNode]?.color}30`,
                          color: (activeExternalService !== null || showExternalAPIs) ? '#667eea' : flowNodes[activeNode]?.color,
                          fontWeight: 500,
                          fontSize: '0.7rem',
                          mt: 0.5,
                        }}
                      />
                    </Box>
                  </Box>
                  
                  <Box sx={{ 
                    color: 'rgba(255, 255, 255, 0.85)', 
                    fontSize: '0.85rem',
                    lineHeight: 1.6,
                    '& strong': { color: 'white', fontWeight: 400 },
                    whiteSpace: 'pre-line'
                  }}>
                    {(showExternalAPIs ? getExternalAPIsDescription() : (activeExternalService !== null ? getExternalServiceDescription(activeExternalService) : getNodeDescription(activeNode))).split('\n').map((line, index) => {
                      if (line.startsWith('•')) {
                        return (
                          <Box key={index} sx={{ 
                            display: 'flex', 
                            alignItems: 'flex-start', 
                            gap: 1, 
                            mb: 0.5,
                            pl: 1 
                          }}>
                            <Box sx={{ 
                              color: (activeExternalService !== null || showExternalAPIs) ? '#667eea' : flowNodes[activeNode]?.color, 
                              fontWeight: 'bold',
                              fontSize: '1rem',
                              lineHeight: 1.4,
                              minWidth: 8
                            }}>
                              •
                            </Box>
                            <Typography variant="body2" sx={{ 
                              color: 'rgba(255, 255, 255, 0.85)', 
                              fontSize: '0.8rem',
                              lineHeight: 1.4,
                              flex: 1
                            }}>
                              {line.slice(2).split(':').map((part, i) => 
                                i === 0 ? (
                                  <span key={i} style={{ fontWeight: 400, color: 'white' }}>{part}:</span>
                                ) : (
                                  <span key={i}>{part}</span>
                                )
                              )}
                            </Typography>
                          </Box>
                        );
                      } else {
                        return (
                          <Typography key={index} variant="body2" sx={{ 
                            color: line.includes(':') ? 'white' : 'rgba(255, 255, 255, 0.85)',
                            fontWeight: 400,
                            fontSize: '0.85rem',
                            mb: 1,
                            lineHeight: 1.5
                          }}>
                            {line}
                          </Typography>
                        );
                      }
                    })}
                  </Box>

                  <Box sx={{ 
                    mt: 3, 
                    pt: 2, 
                    borderTop: `1px solid ${(activeExternalService !== null || showExternalAPIs) ? '#667eea' : flowNodes[activeNode]?.color}30`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}>
                    <Typography variant="caption" sx={{ 
                      color: `${(activeExternalService !== null || showExternalAPIs) ? '#667eea' : flowNodes[activeNode]?.color}dd`, 
                      fontWeight: 400,
                      fontSize: '0.75rem'
                    }}>
                      {(activeExternalService !== null || showExternalAPIs) ? 'External Service Integration' : 'Technical Process Details'}
                    </Typography>
                    <Box sx={{ 
                      width: 8, 
                      height: 8, 
                      borderRadius: '50%', 
                      backgroundColor: (activeExternalService !== null || showExternalAPIs) ? '#667eea' : flowNodes[activeNode]?.color,
                      opacity: 0.7 
                    }} />
                  </Box>
                </Box>
              )}

              {/* External Services Labels */}
              <Box sx={{ position: 'absolute', top: 120, left: 60 }}>
                <Chip
                  icon={<DatabaseIcon sx={{ fontSize: 16 }} />}
                  label="External APIs"
                  size="medium"
                  clickable
                  onClick={handleExternalAPIsClick}
                  sx={{ 
                    backgroundColor: showExternalAPIs ? 'rgba(102, 126, 234, 0.2)' : 'rgba(255, 255, 255, 0.12)', 
                    color: showExternalAPIs ? '#667eea' : 'rgba(255, 255, 255, 0.8)',
                    fontWeight: 400,
                    borderRadius: 4,
                    px: 2,
                    py: 0.5,
                    fontSize: '0.75rem',
                    border: showExternalAPIs ? '1px solid rgba(102, 126, 234, 0.4)' : '1px solid rgba(255, 255, 255, 0.2)',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      backgroundColor: 'rgba(102, 126, 234, 0.15)',
                      color: '#667eea',
                      border: '1px solid rgba(102, 126, 234, 0.3)',
                    }
                  }}
                />
              </Box>

              {/* Center Flow Label */}
              <Box sx={{ position: 'absolute', top: 15, left: 290 }}>
                <Chip
                  icon={<MagicIcon sx={{ fontSize: 18 }} />}
                  label="MemeVoiceClone-inator Pipeline"
                  size="medium"
                  sx={{ 
                    backgroundColor: 'rgba(102, 126, 234, 0.15)', 
                    color: 'white',
                    fontWeight: 400,
                    borderRadius: 4,
                    px: 3,
                    py: 1,
                    fontSize: '0.8rem',
                    border: '1px solid rgba(102, 126, 234, 0.3)',
                    boxShadow: '0 2px 8px rgba(102, 126, 234, 0.2)'
                  }}
                />
              </Box>


            </Box>
          </CardContent>
        </Card>

      </Container>
    </Box>
  );
}; 