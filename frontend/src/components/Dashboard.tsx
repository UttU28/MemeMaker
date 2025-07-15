import React, { useState } from 'react';
import {
  Box,
  Typography,
  Container,
  AppBar,
  Toolbar,
  Button,
  Avatar,
  Fade,
  Paper,
  Slide,
  Grow,
} from '@mui/material';
import {
  PlayArrow,
  PlayCircle,
  VolumeUp,
  VolumeOff,
  Favorite,
  ChatBubble,
  Send,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { ProjectShowcase } from './ProjectShowcase';

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
          <Box sx={{ mb: 10, textAlign: 'center' }}>
            <Box
              sx={{
                display: 'grid',
                gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
                gap: 8,
                maxWidth: 1100,
                mx: 'auto',
                position: 'relative',
                px: 2,
              }}
            >
              {/* Video Player 1 */}
              <Grow in timeout={1500}>
                <Box sx={{ position: 'relative' }}>
                  {/* Floating Script Bubble */}
                  <Box
                    sx={{
                      position: 'absolute',
                      top: -20,
                      left: -10,
                      zIndex: 10,
                      background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.95) 100%)',
                      backdropFilter: 'blur(20px)',
                      borderRadius: 3,
                      px: 3,
                      py: 2,
                      maxWidth: 280,
                      border: '1px solid rgba(148, 163, 184, 0.3)',
                      boxShadow: '0 10px 30px rgba(0, 0, 0, 0.3)',
                      transform: 'rotate(-2deg)',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'rotate(0deg) translateY(-5px)',
                        boxShadow: '0 15px 40px rgba(0, 0, 0, 0.4)',
                      },
                    }}
                  >
                    <Typography variant="body2" sx={{ color: 'white', lineHeight: 1.4, fontSize: '0.85rem' }}>
                      <Box component="span" sx={{ color: 'text.secondary', fontWeight: 600 }}>
                        Script:
                      </Box>
                      {' '}
                      <Box component="span" sx={{ fontStyle: 'italic', color: 'rgba(255, 255, 255, 0.9)' }}>
                        "How to create an app, give roadmap and monetize it"
                      </Box>
                    </Typography>
                  </Box>

                  {/* Floating Characters Bubble */}
                  <Box
                    sx={{
                      position: 'absolute',
                      bottom: -15,
                      right: -15,
                      zIndex: 10,
                      background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.95) 0%, rgba(139, 92, 246, 0.95) 100%)',
                      backdropFilter: 'blur(20px)',
                      borderRadius: 3,
                      px: 3,
                      py: 2,
                      border: '1px solid rgba(99, 102, 241, 0.5)',
                      boxShadow: '0 10px 30px rgba(99, 102, 241, 0.3)',
                      transform: 'rotate(2deg)',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'rotate(0deg) translateY(-5px)',
                        boxShadow: '0 15px 40px rgba(99, 102, 241, 0.4)',
                      },
                    }}
                  >
                    <Typography variant="body2" sx={{ color: 'white', lineHeight: 1.4, fontSize: '0.85rem' }}>
                      <Box component="span" sx={{ color: 'rgba(255, 255, 255, 0.9)', fontWeight: 600 }}>
                        Characters:
                      </Box>
                      {' '}
                      <Box component="span" sx={{ color: 'rgba(255, 255, 255, 0.85)' }}>
                        Peter Griffin, Stewie Griffin
                      </Box>
                    </Typography>
                  </Box>
                  
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
                <Box sx={{ position: 'relative' }}>
                  {/* Floating Script Bubble */}
                  <Box
                    sx={{
                      position: 'absolute',
                      top: -20,
                      left: -10,
                      zIndex: 10,
                      background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.95) 100%)',
                      backdropFilter: 'blur(20px)',
                      borderRadius: 3,
                      px: 3,
                      py: 2,
                      maxWidth: 280,
                      border: '1px solid rgba(148, 163, 184, 0.3)',
                      boxShadow: '0 10px 30px rgba(0, 0, 0, 0.3)',
                      transform: 'rotate(-2deg)',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'rotate(0deg) translateY(-5px)',
                        boxShadow: '0 15px 40px rgba(0, 0, 0, 0.4)',
                      },
                    }}
                  >
                    <Typography variant="body2" sx={{ color: 'white', lineHeight: 1.4, fontSize: '0.85rem' }}>
                      <Box component="span" sx={{ color: 'text.secondary', fontWeight: 600 }}>
                        Script:
                      </Box>
                      {' '}
                      <Box component="span" sx={{ fontStyle: 'italic', color: 'rgba(255, 255, 255, 0.9)' }}>
                        "How does Tesla Autopilot car works?"
                      </Box>
                    </Typography>
                  </Box>

                  {/* Floating Characters Bubble */}
                  <Box
                    sx={{
                      position: 'absolute',
                      bottom: -15,
                      right: -15,
                      zIndex: 10,
                      background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.95) 0%, rgba(139, 92, 246, 0.95) 100%)',
                      backdropFilter: 'blur(20px)',
                      borderRadius: 3,
                      px: 3,
                      py: 2,
                      border: '1px solid rgba(16, 185, 129, 0.5)',
                      boxShadow: '0 10px 30px rgba(16, 185, 129, 0.3)',
                      transform: 'rotate(2deg)',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'rotate(0deg) translateY(-5px)',
                        boxShadow: '0 15px 40px rgba(16, 185, 129, 0.4)',
                      },
                    }}
                  >
                    <Typography variant="body2" sx={{ color: 'white', lineHeight: 1.4, fontSize: '0.85rem' }}>
                      <Box component="span" sx={{ color: 'rgba(255, 255, 255, 0.9)', fontWeight: 600 }}>
                        Characters:
                      </Box>
                      {' '}
                      <Box component="span" sx={{ color: 'rgba(255, 255, 255, 0.85)' }}>
                        Rick Sanchez, Morty Smith
                      </Box>
                    </Typography>
                  </Box>

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
            <Box sx={{ textAlign: 'center', mt: 8 }}>
              <Button
                variant="contained"
                size="large"
                startIcon={<PlayArrow />}
                onClick={handleStartCreating}
                sx={{
                  px: 6,
                  py: 2,
                  fontSize: '1.2rem',
                  fontWeight: 600,
                  borderRadius: 4,
                  background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                  boxShadow: '0 10px 30px rgba(99, 102, 241, 0.3)',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
                    transform: 'translateY(-3px)',
                    boxShadow: '0 15px 40px rgba(99, 102, 241, 0.4)',
                  },
                }}
              >
                Start Creating
              </Button>
              
            </Box>
          </Box>
        </Fade>

        {/* Why I Built This */}
        <ProjectShowcase />

      </Container>
    </Box>
  );
};

export default Dashboard; 