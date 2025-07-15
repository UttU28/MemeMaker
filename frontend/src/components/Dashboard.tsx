import React, { useState } from 'react';
import {
  Box,
  Typography,
  Container,
  Card,
  CardContent,
  AppBar,
  Toolbar,
  Button,
  Stack,
  Avatar,
  Fade,
  Zoom,
  Paper,
  Slide,
  Grow,
} from '@mui/material';
import {
  People as PeopleIcon,
  Description as ScriptIcon,
  VideoLibrary as VideoIcon,
  PlayArrow,
  Mic,
  PlayCircle,
  VolumeUp,
  VolumeOff,
  Favorite,
  ChatBubble,
  Send,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const steps = [
  {
    step: "1",
    icon: <PeopleIcon sx={{ fontSize: 40 }} />,
    title: 'Create Characters',
    description: 'Upload audio samples and character images to create AI-powered voice clones using F5-TTS technology.',
    color: '#6366f1',
  },
  {
    step: "2", 
    icon: <ScriptIcon sx={{ fontSize: 40 }} />,
    title: 'Generate Scripts',
    description: 'Create engaging dialogues and scripts for your characters to bring your meme ideas to life.',
    color: '#f59e0b',
  },
  {
    step: "3",
    icon: <VideoIcon sx={{ fontSize: 40 }} />,
    title: 'Generate Videos',
    description: 'Combine voice clones, scripts, and visuals into viral meme videos ready to share.',
    color: '#10b981',
  },
];

const Dashboard: React.FC = () => {
  const [playingVideo1, setPlayingVideo1] = useState(false);
  const [playingVideo2, setPlayingVideo2] = useState(false);
  const [mutedVideo1, setMutedVideo1] = useState(false);
  const [mutedVideo2, setMutedVideo2] = useState(false);
  const navigate = useNavigate();

  const handleStartCreating = () => {
    navigate('/auth');
  };

  const handlePlayVideo1 = () => {
    setPlayingVideo1(!playingVideo1);
  };

  const handlePlayVideo2 = () => {
    setPlayingVideo2(!playingVideo2);
  };

  const handleMuteVideo1 = () => {
    setMutedVideo1(!mutedVideo1);
  };

  const handleMuteVideo2 = () => {
    setMutedVideo2(!mutedVideo2);
  };

  return (
    <Box sx={{ minHeight: '100vh' }}>
      {/* Header */}
      <AppBar position="static" elevation={0}>
        <Toolbar>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
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
        </Toolbar>
      </AppBar>

      {/* Hero Section */}
      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Fade in timeout={1000}>
          <Box sx={{ textAlign: 'center', mb: 6 }}>
            <Typography variant="h1" component="h1" gutterBottom sx={{ mb: 2 }}>
              Create Viral Memes
            </Typography>
            <Typography
              variant="h5"
              component="h2"
              sx={{
                mb: 4,
                color: 'text.secondary',
                maxWidth: 600,
                mx: 'auto',
                lineHeight: 1.6,
              }}
            >
              Create viral memes in just 2 steps and get massive reach for FREE! 
            </Typography>
          </Box>
        </Fade>

        {/* Showcase Section */}
        <Fade in timeout={1200}>
          <Box sx={{ mb: 8, textAlign: 'center' }}>
            <Box
              sx={{
                display: 'grid',
                gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
                gap: 4,
                maxWidth: 900,
                mx: 'auto',
              }}
            >
              {/* Video Player 1 */}
              <Grow in timeout={1500}>
                <Box>
                  {/* Sample Script for Video 1 */}
                  <Paper
                    elevation={0}
                    sx={{
                      mb: 2,
                      p: 2,
                      background: 'rgba(30, 41, 59, 0.4)',
                      border: '1px solid rgba(148, 163, 184, 0.2)',
                      borderRadius: 2,
                    }}
                  >
                    <Typography variant="body2" sx={{ color: 'white', lineHeight: 1.6 }}>
                      <Box component="span" sx={{ color: 'text.secondary', fontWeight: 600 }}>
                        Input Script:
                      </Box>
                      {' '}
                      <Box component="span" sx={{ fontStyle: 'italic' }}>
                        "Peter and Stewie on how to create an app, give roadmap and monetize it"
                      </Box>
                    </Typography>
                  </Paper>
                  
                <Paper
                  elevation={0}
                  sx={{
                    position: 'relative',
                    aspectRatio: '9/16',
                      maxWidth: 280,
                      mx: 'auto',
                      borderRadius: 4,
                    overflow: 'hidden',
                      background: 'rgba(30, 41, 59, 0.8)',
                    backdropFilter: 'blur(20px)',
                      border: '2px solid rgba(148, 163, 184, 0.2)',
                    cursor: 'pointer',
                      transition: 'all 0.4s ease',
                    '&:hover': {
                        transform: 'translateY(-10px)',
                        boxShadow: '0 25px 50px rgba(99, 102, 241, 0.3)',
                        border: '2px solid rgba(99, 102, 241, 0.5)',
                      },
                    }}
                    onClick={handlePlayVideo1}
                  >
                    {playingVideo1 ? (
                      <>
                    <Box
                      component="video"
                          src="/video2.mp4"
                      autoPlay
                          muted={mutedVideo1}
                      sx={{
                        width: '100%',
                        height: '100%',
                        objectFit: 'cover',
                      }}
                    />
                        <Box
                          sx={{
                            position: 'absolute',
                            top: 16,
                            right: 16,
                            background: 'rgba(0, 0, 0, 0.8)',
                            borderRadius: '50%',
                            width: 48,
                            height: 48,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease',
                            '&:hover': {
                              background: 'rgba(99, 102, 241, 0.8)',
                              transform: 'scale(1.1)',
                            },
                          }}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleMuteVideo1();
                          }}
                        >
                          {mutedVideo1 ? (
                            <VolumeOff sx={{ fontSize: 24, color: 'white' }} />
                          ) : (
                            <VolumeUp sx={{ fontSize: 24, color: 'white' }} />
                          )}
                        </Box>
                        
                        {/* Instagram-style interactions */}
                        <Box
                          sx={{
                            position: 'absolute',
                            right: 12,
                            bottom: 60,
                            display: 'flex',
                            flexDirection: 'column',
                            gap: 2,
                            alignItems: 'center',
                          }}
                        >
                          {/* Like */}
                          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                            <Box
                              sx={{
                                background: 'rgba(0, 0, 0, 0.6)',
                                borderRadius: '50%',
                                width: 40,
                                height: 40,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                cursor: 'pointer',
                                transition: 'all 0.3s ease',
                                '&:hover': {
                                  background: 'rgba(255, 255, 255, 0.2)',
                                  transform: 'scale(1.1)',
                                },
                              }}
                              onClick={(e) => e.stopPropagation()}
                            >
                              <Favorite sx={{ fontSize: 22, color: '#ff1744' }} />
                            </Box>
                            <Typography variant="caption" sx={{ color: 'white', fontWeight: 600, mt: 0.3, fontSize: '0.7rem' }}>
                              2.3M
                            </Typography>
                          </Box>

                          {/* Comment */}
                          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                            <Box
                              sx={{
                                background: 'rgba(0, 0, 0, 0.6)',
                                borderRadius: '50%',
                                width: 40,
                                height: 40,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                cursor: 'pointer',
                                transition: 'all 0.3s ease',
                                '&:hover': {
                                  background: 'rgba(255, 255, 255, 0.2)',
                                  transform: 'scale(1.1)',
                                },
                              }}
                              onClick={(e) => e.stopPropagation()}
                            >
                              <ChatBubble sx={{ fontSize: 22, color: 'white' }} />
                            </Box>
                            <Typography variant="caption" sx={{ color: 'white', fontWeight: 600, mt: 0.3, fontSize: '0.7rem' }}>
                              85K
                            </Typography>
                          </Box>

                          {/* Send */}
                          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                            <Box
                              sx={{
                                background: 'rgba(0, 0, 0, 0.6)',
                                borderRadius: '50%',
                                width: 40,
                                height: 40,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                cursor: 'pointer',
                                transition: 'all 0.3s ease',
                                '&:hover': {
                                  background: 'rgba(255, 255, 255, 0.2)',
                                  transform: 'scale(1.1)',
                                },
                              }}
                              onClick={(e) => e.stopPropagation()}
                            >
                              <Send sx={{ fontSize: 22, color: 'white' }} />
                            </Box>
                            <Typography variant="caption" sx={{ color: 'white', fontWeight: 600, mt: 0.3, fontSize: '0.7rem' }}>
                              156K
                            </Typography>
                          </Box>
                        </Box>
                      </>
                  ) : (
                    <>
                      <Box
                        component="img"
                        src="/showcase-frame1.jpg"
                          alt="Sample meme video 1"
                        sx={{
                          width: '100%',
                          height: '100%',
                          objectFit: 'cover',
                            transition: 'transform 0.4s ease',
                            display: 'block',
                          '&:hover': {
                              transform: 'scale(1.1)',
                          },
                        }}
                      />
                      <Box
                        sx={{
                          position: 'absolute',
                          top: '50%',
                          left: '50%',
                          transform: 'translate(-50%, -50%)',
                            background: 'rgba(0, 0, 0, 0.8)',
                          borderRadius: '50%',
                            width: 90,
                            height: 90,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                            transition: 'all 0.4s ease',
                            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
                          '&:hover': {
                              background: 'rgba(99, 102, 241, 0.8)',
                              transform: 'translate(-50%, -50%) scale(1.2)',
                          },
                        }}
                      >
                          <PlayCircle sx={{ fontSize: 50, color: 'white' }} />
                        </Box>
                        
                        {/* Instagram-style interactions on thumbnail */}
                        <Box
                          sx={{
                            position: 'absolute',
                            right: 12,
                            bottom: 60,
                            display: 'flex',
                            flexDirection: 'column',
                            gap: 2,
                            alignItems: 'center',
                          }}
                        >
                          {/* Like */}
                          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                            <Box
                              sx={{
                                background: 'rgba(0, 0, 0, 0.6)',
                                borderRadius: '50%',
                                width: 40,
                                height: 40,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                cursor: 'pointer',
                                transition: 'all 0.3s ease',
                                '&:hover': {
                                  background: 'rgba(255, 255, 255, 0.2)',
                                  transform: 'scale(1.1)',
                                },
                              }}
                              onClick={(e) => e.stopPropagation()}
                            >
                              <Favorite sx={{ fontSize: 22, color: '#ff1744' }} />
                            </Box>
                            <Typography variant="caption" sx={{ color: 'white', fontWeight: 600, mt: 0.3, fontSize: '0.7rem' }}>
                              2.3M
                            </Typography>
                          </Box>

                          {/* Comment */}
                          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                            <Box
                              sx={{
                                background: 'rgba(0, 0, 0, 0.6)',
                                borderRadius: '50%',
                                width: 40,
                                height: 40,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                cursor: 'pointer',
                                transition: 'all 0.3s ease',
                                '&:hover': {
                                  background: 'rgba(255, 255, 255, 0.2)',
                                  transform: 'scale(1.1)',
                                },
                              }}
                              onClick={(e) => e.stopPropagation()}
                            >
                              <ChatBubble sx={{ fontSize: 22, color: 'white' }} />
                            </Box>
                            <Typography variant="caption" sx={{ color: 'white', fontWeight: 600, mt: 0.3, fontSize: '0.7rem' }}>
                              85K
                            </Typography>
                          </Box>

                          {/* Send */}
                          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                            <Box
                              sx={{
                                background: 'rgba(0, 0, 0, 0.6)',
                                borderRadius: '50%',
                                width: 40,
                                height: 40,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                cursor: 'pointer',
                                transition: 'all 0.3s ease',
                                '&:hover': {
                                  background: 'rgba(255, 255, 255, 0.2)',
                                  transform: 'scale(1.1)',
                                },
                              }}
                              onClick={(e) => e.stopPropagation()}
                            >
                              <Send sx={{ fontSize: 22, color: 'white' }} />
                            </Box>
                            <Typography variant="caption" sx={{ color: 'white', fontWeight: 600, mt: 0.3, fontSize: '0.7rem' }}>
                              156K
                            </Typography>
                          </Box>
                      </Box>
                    </>
                  )}
                    
                  </Paper>
                </Box>
              </Grow>

              {/* Video Player 2 */}
              <Slide direction="left" in timeout={1800}>
                <Box>
                  {/* Sample Script for Video 2 */}
                  <Paper
                    elevation={0}
                    sx={{
                      mb: 2,
                      p: 2,
                      background: 'rgba(30, 41, 59, 0.4)',
                      border: '1px solid rgba(148, 163, 184, 0.2)',
                      borderRadius: 2,
                    }}
                  >
                    <Typography variant="body2" sx={{ color: 'white', lineHeight: 1.6 }}>
                      <Box component="span" sx={{ color: 'text.secondary', fontWeight: 600 }}>
                        Input Script:
                      </Box>
                      {' '}
                      <Box component="span" sx={{ fontStyle: 'italic' }}>
                        "Rick and Morty discussing how Tesla Autopilot car works"
                      </Box>
                    </Typography>
                </Paper>

                  <Paper
                    elevation={0}
                    sx={{
                      position: 'relative',
                      aspectRatio: '9/16',
                      maxWidth: 280,
                      mx: 'auto',
                      borderRadius: 4,
                      overflow: 'hidden',
                      background: 'rgba(30, 41, 59, 0.8)',
                      backdropFilter: 'blur(20px)',
                      border: '2px solid rgba(148, 163, 184, 0.2)',
                      cursor: 'pointer',
                      transition: 'all 0.4s ease',
                      '&:hover': {
                        transform: 'translateY(-10px)',
                        boxShadow: '0 25px 50px rgba(16, 185, 129, 0.3)',
                        border: '2px solid rgba(16, 185, 129, 0.5)',
                      },
                    }}
                    onClick={handlePlayVideo2}
                  >
                    {playingVideo2 ? (
                      <>
                        <Box
                          component="video"
                          src="/video3.mp4"
                          autoPlay
                          muted={mutedVideo2}
                          sx={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover',
                          }}
                        />
                        <Box
                          sx={{
                            position: 'absolute',
                            top: 16,
                            right: 16,
                            background: 'rgba(0, 0, 0, 0.8)',
                            borderRadius: '50%',
                            width: 48,
                            height: 48,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease',
                            '&:hover': {
                              background: 'rgba(16, 185, 129, 0.8)',
                              transform: 'scale(1.1)',
                            },
                          }}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleMuteVideo2();
                          }}
                        >
                          {mutedVideo2 ? (
                            <VolumeOff sx={{ fontSize: 24, color: 'white' }} />
                          ) : (
                            <VolumeUp sx={{ fontSize: 24, color: 'white' }} />
                          )}
                        </Box>
                        
                        {/* Instagram-style interactions */}
                        <Box
                          sx={{
                            position: 'absolute',
                            right: 12,
                            bottom: 60,
                            display: 'flex',
                            flexDirection: 'column',
                            gap: 2,
                            alignItems: 'center',
                          }}
                        >
                          {/* Like */}
                          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                            <Box
                              sx={{
                                background: 'rgba(0, 0, 0, 0.6)',
                                borderRadius: '50%',
                                width: 40,
                                height: 40,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                cursor: 'pointer',
                                transition: 'all 0.3s ease',
                                '&:hover': {
                                  background: 'rgba(255, 255, 255, 0.2)',
                                  transform: 'scale(1.1)',
                                },
                              }}
                              onClick={(e) => e.stopPropagation()}
                            >
                              <Favorite sx={{ fontSize: 22, color: '#ff1744' }} />
                            </Box>
                            <Typography variant="caption" sx={{ color: 'white', fontWeight: 600, mt: 0.3, fontSize: '0.7rem' }}>
                              1M
                            </Typography>
                          </Box>

                          {/* Comment */}
                          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                            <Box
                              sx={{
                                background: 'rgba(0, 0, 0, 0.6)',
                                borderRadius: '50%',
                                width: 40,
                                height: 40,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                cursor: 'pointer',
                                transition: 'all 0.3s ease',
                                '&:hover': {
                                  background: 'rgba(255, 255, 255, 0.2)',
                                  transform: 'scale(1.1)',
                                },
                              }}
                              onClick={(e) => e.stopPropagation()}
                            >
                              <ChatBubble sx={{ fontSize: 22, color: 'white' }} />
                            </Box>
                            <Typography variant="caption" sx={{ color: 'white', fontWeight: 600, mt: 0.3, fontSize: '0.7rem' }}>
                              10K
                            </Typography>
                          </Box>

                          {/* Send */}
                          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                            <Box
                              sx={{
                                background: 'rgba(0, 0, 0, 0.6)',
                                borderRadius: '50%',
                                width: 40,
                                height: 40,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                cursor: 'pointer',
                                transition: 'all 0.3s ease',
                                '&:hover': {
                                  background: 'rgba(255, 255, 255, 0.2)',
                                  transform: 'scale(1.1)',
                                },
                              }}
                              onClick={(e) => e.stopPropagation()}
                            >
                              <Send sx={{ fontSize: 22, color: 'white' }} />
                            </Box>
                            <Typography variant="caption" sx={{ color: 'white', fontWeight: 600, mt: 0.3, fontSize: '0.7rem' }}>
                              47K
                            </Typography>
                          </Box>
                        </Box>
                      </>
                    ) : (
                      <>
                    <Box
                      component="img"
                      src="/showcase-frame3.jpg"
                          alt="Sample meme video 2"
                      sx={{
                        width: '100%',
                        height: '100%',
                        objectFit: 'cover',
                            transition: 'transform 0.4s ease',
                            display: 'block',
                        '&:hover': {
                              transform: 'scale(1.1)',
                        },
                      }}
                    />
                        <Box
                          sx={{
                            position: 'absolute',
                            top: '50%',
                            left: '50%',
                            transform: 'translate(-50%, -50%)',
                            background: 'rgba(0, 0, 0, 0.8)',
                            borderRadius: '50%',
                            width: 90,
                            height: 90,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            transition: 'all 0.4s ease',
                            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
                            '&:hover': {
                              background: 'rgba(16, 185, 129, 0.8)',
                              transform: 'translate(-50%, -50%) scale(1.2)',
                            },
                          }}
                        >
                          <PlayCircle sx={{ fontSize: 50, color: 'white' }} />
                        </Box>
                        
                        {/* Instagram-style interactions on thumbnail */}
                        <Box
                          sx={{
                            position: 'absolute',
                            right: 12,
                            bottom: 60,
                            display: 'flex',
                            flexDirection: 'column',
                            gap: 2,
                            alignItems: 'center',
                          }}
                        >
                          {/* Like */}
                          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                            <Box
                              sx={{
                                background: 'rgba(0, 0, 0, 0.6)',
                                borderRadius: '50%',
                                width: 40,
                                height: 40,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                cursor: 'pointer',
                                transition: 'all 0.3s ease',
                                '&:hover': {
                                  background: 'rgba(255, 255, 255, 0.2)',
                                  transform: 'scale(1.1)',
                                },
                              }}
                              onClick={(e) => e.stopPropagation()}
                            >
                              <Favorite sx={{ fontSize: 22, color: '#ff1744' }} />
                            </Box>
                            <Typography variant="caption" sx={{ color: 'white', fontWeight: 600, mt: 0.3, fontSize: '0.7rem' }}>
                              1M
                            </Typography>
                          </Box>

                          {/* Comment */}
                          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                            <Box
                              sx={{
                                background: 'rgba(0, 0, 0, 0.6)',
                                borderRadius: '50%',
                                width: 40,
                                height: 40,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                cursor: 'pointer',
                                transition: 'all 0.3s ease',
                                '&:hover': {
                                  background: 'rgba(255, 255, 255, 0.2)',
                                  transform: 'scale(1.1)',
                                },
                              }}
                              onClick={(e) => e.stopPropagation()}
                            >
                              <ChatBubble sx={{ fontSize: 22, color: 'white' }} />
                            </Box>
                            <Typography variant="caption" sx={{ color: 'white', fontWeight: 600, mt: 0.3, fontSize: '0.7rem' }}>
                              10K
                            </Typography>
                          </Box>

                          {/* Send */}
                          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                            <Box
                              sx={{
                                background: 'rgba(0, 0, 0, 0.6)',
                                borderRadius: '50%',
                                width: 40,
                                height: 40,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                cursor: 'pointer',
                                transition: 'all 0.3s ease',
                                '&:hover': {
                                  background: 'rgba(255, 255, 255, 0.2)',
                                  transform: 'scale(1.1)',
                                },
                              }}
                              onClick={(e) => e.stopPropagation()}
                            >
                              <Send sx={{ fontSize: 22, color: 'white' }} />
                            </Box>
                            <Typography variant="caption" sx={{ color: 'white', fontWeight: 600, mt: 0.3, fontSize: '0.7rem' }}>
                              47K
                            </Typography>
                          </Box>
                        </Box>
                      </>
                    )}

                  </Paper>
                </Box>
                </Slide>
            </Box>
            
            {/* Start Creating Button */}
            <Box sx={{ textAlign: 'center', mt: 6 }}>
              <Button
                variant="contained"
                size="large"
                startIcon={<PlayArrow />}
                onClick={handleStartCreating}
                sx={{
                  px: 4,
                  py: 1.5,
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
                    transform: 'translateY(-2px)',
                  },
                }}
              >
                Start Creating
              </Button>
              
              {/* Demo Project Notice */}
              <Box sx={{ mt: 4, maxWidth: 800, mx: 'auto' }}>
                <Typography
                  variant="h6"
                  sx={{
                    color: 'text.secondary',
                    fontWeight: 500,
                    mb: 2,
                    fontSize: '1.1rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: 1,
                  }}
                >
                  <WarningIcon sx={{ color: '#f59e0b', fontSize: '1.3rem' }} />
                  Demo Project Showcase
                </Typography>
                <Typography
                  variant="body1"
                  sx={{
                    color: 'text.secondary',
                    lineHeight: 1.7,
                    fontSize: '1rem',
                    maxWidth: 900,
                    mx: 'auto',
                  }}
                >
                  This is a demonstration of my technical skills in building a complete meme creation pipeline. 
                  The project showcases automated content generation, voice cloning integration with F5-TTS, 
                  video processing workflows, and scalable architecture for daily meme production and social media distribution. 
                  Built as a proof-of-concept to demonstrate full-stack development capabilities, 
                  AI integration, and content automation systems.
                </Typography>
                <Typography
                  variant="body2"
                      sx={{
                    color: 'text.disabled',
                    mt: 2,
                    fontStyle: 'italic',
                    fontSize: '0.9rem',
                  }}
                >
                  Created to explore the intersection of AI, automation, and viral content creation.
                </Typography>
              </Box>
            </Box>
          </Box>
        </Fade>

        {/* How to Use Our Platform */}
        <Box sx={{ mb: 8 }}>
          <Typography
            variant="h3"
            component="h2"
            sx={{
              textAlign: 'center',
              mb: 2,
              background: 'linear-gradient(135deg, #f1f5f9 0%, #94a3b8 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}
          >
            How to Use Our Platform
          </Typography>
          <Typography
            variant="h6"
            sx={{
              textAlign: 'center',
              mb: 6,
              color: 'text.secondary',
              maxWidth: 500,
              mx: 'auto',
            }}
          >
            Simple 3-step process to create viral voice cloning memes
          </Typography>

          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: {
                xs: 'repeat(1, 1fr)',
                md: 'repeat(3, 1fr)',
              },
              gap: 3,
            }}
          >
            {steps.map((step, index) => (
              <Zoom in timeout={500 + index * 200} key={index}>
                <Card
                  sx={{
                    height: '100%',
                    cursor: 'pointer',
                    position: 'relative',
                    overflow: 'hidden',
                    background: 'rgba(30, 41, 59, 0.6)',
                    backdropFilter: 'blur(20px)',
                    border: '1px solid rgba(148, 163, 184, 0.1)',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-8px)',
                      border: '1px solid rgba(99, 102, 241, 0.3)',
                      boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
                    },
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: '4px',
                      background: `linear-gradient(135deg, ${step.color} 0%, ${step.color}CC 100%)`,
                    },
                  }}
                >
                  <CardContent sx={{ p: 4, height: '100%', textAlign: 'center' }}>
                    <Box sx={{ position: 'relative', mb: 3 }}>
                      <Avatar 
                      sx={{
                          mx: 'auto',
                          width: 64, 
                          height: 64,
                          background: `linear-gradient(135deg, ${step.color} 0%, ${step.color}CC 100%)`,
                          mb: 2,
                        }}
                      >
                        {step.icon}
                      </Avatar>
                      <Box
                        sx={{
                          position: 'absolute',
                          top: -8,
                          right: 'calc(50% - 40px)',
                          width: 24,
                          height: 24,
                          borderRadius: '50%',
                          background: step.color,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: 'white',
                          fontWeight: 'bold',
                          fontSize: '0.875rem',
                        }}
                      >
                        {step.step}
                      </Box>
                    </Box>
                    <Typography variant="h5" component="h3" sx={{ mb: 2, fontWeight: 600 }}>
                      {step.title}
                    </Typography>
                    <Typography variant="body1" sx={{ color: 'text.secondary', lineHeight: 1.6 }}>
                      {step.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Zoom>
            ))}
          </Box>
        </Box>

      </Container>
    </Box>
  );
};

export default Dashboard; 