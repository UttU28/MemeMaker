import React, { useState } from 'react';
import {
  Box,
  Typography,
  Container,
  Paper,
  Avatar,
  Button,
  Fade,
  Zoom,
  TextField,
} from '@mui/material';
import {
  YouTube as YouTubeIcon,
  Whatshot as WhatshotIcon,
  Send as SendIcon,
} from '@mui/icons-material';
import { DashboardLayout } from '../components/DashboardLayout';

export const AboutUsPage: React.FC = () => {
  const [userMessage, setUserMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('User message:', userMessage);
    // Clear the input after submission
    setUserMessage('');
  };

  return (
    <DashboardLayout>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Fade in timeout={800}>
          <Box>
            {/* Header Section */}
            <Box sx={{ textAlign: 'center', mb: 6 }}>
              <Typography 
                variant="h3" 
                component="h1" 
                sx={{ 
                  mb: 2,
                  background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                  fontWeight: 800,
                }}
              >
                About Us
              </Typography>
            </Box>

            {/* Platform Overview */}
            <Box sx={{ 
              display: 'flex',
              justifyContent: 'center',
              mb: 6 
            }}>
              <Zoom in timeout={600}>
                <Paper 
                  elevation={0}
                  sx={{ 
                    p: 4, 
                    textAlign: 'center',
                    width: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center',
                  }}
                >
                <Typography 
                  variant="h4" 
                  component="h2" 
                  sx={{ 
                    mb: 4,
                    fontWeight: 700,
                    background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                  }}
                >
                    Why We Built This
                </Typography>
                  <Typography variant="body1" color="text.secondary" sx={{ lineHeight: 1.7 }}>
                    This platform was built for fun! I saw all the memes getting viral and wanted in on the action. After creating the entire pipeline, I got bored... so now I'm showcasing it for everyone to use and create their own viral content! A revolutionary platform that lets you create viral memes in just 2 simple steps! Choose from AI-powered characters, generate engaging scripts automatically, and watch your content go viral. Get massive reach without any technical skills or expensive equipment.
                  </Typography>
                </Paper>
              </Zoom>
            </Box>

            {/* Let's Connect Section */}
            <Paper elevation={0} sx={{ p: 4, mb: 6 }}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography 
                  variant="h4" 
                  component="h2" 
                  sx={{ 
                    mb: 4,
                    fontWeight: 700,
                    background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                  }}
                >
                  Let's Connect & Build Together
                </Typography>
                
                <Typography 
                  variant="body1" 
                  color="text.secondary" 
                  sx={{ 
                    mb: 4,
                    lineHeight: 1.7,
                    opacity: 0.9,
                  }}
                >
                  Let's be honest - this isn't some breakthrough technology! I'm using F5-TTS for the voice cloning (which is the main part of the magic) and FFMPEG for creating and stitching the videos together. Everything is currently running on my home server, that's why I'm giving free credits and free trial as of now.
                </Typography>

                <Typography 
                  variant="body1" 
                  color="text.secondary" 
                  sx={{ 
                    mb: 4,
                    lineHeight: 1.7,
                    opacity: 0.9,
                  }}
                >
                  This is pretty heavy on resources, so we'll probably be running for just a week and shutting it down if there's no interest. If you want in on this action or wanna keep using it, lemme know and I'll figure something out! Just comment down what you think and let's connect and build something good together.
                </Typography>

                <Box 
                  component="form" 
                  onSubmit={handleSubmit}
                  sx={{ 
                    width: '100%'
                  }}
                >
                  <TextField
                    fullWidth
                    multiline
                    rows={4}
                    variant="outlined"
                    placeholder="🚀 Tell me your crazy ideas, roast my code, or just say hi - I promise I'll read it! What's on your mind?"
                    value={userMessage}
                    onChange={(e) => setUserMessage(e.target.value)}
                    sx={{
                      mb: 2,
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: 'rgba(30, 41, 59, 0.5)',
                        borderRadius: '12px',
                        '& fieldset': {
                          borderColor: 'rgba(99, 102, 241, 0.3)',
                        },
                        '&:hover fieldset': {
                          borderColor: 'rgba(99, 102, 241, 0.5)',
                        },
                        '&.Mui-focused fieldset': {
                          borderColor: 'primary.main',
                        },
                      },
                      '& .MuiInputBase-input': {
                        color: 'text.primary',
                        '&::placeholder': {
                          color: 'text.secondary',
                          opacity: 0.8,
                        },
                      },
                    }}
                  />
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                    <Button
                      type="submit"
                      variant="contained"
                      disabled={!userMessage.trim()}
                      startIcon={<SendIcon />}
                      sx={{
                        background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                        color: 'white',
                        fontWeight: 600,
                        px: 3,
                        py: 1.5,
                        minWidth: 120,
                        '&:hover': {
                          background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
                          transform: 'translateY(-2px)',
                        },
                        '&:disabled': {
                          background: 'rgba(148, 163, 184, 0.3)',
                          color: 'rgba(255, 255, 255, 0.5)',
                        },
                      }}
                    >
                      Send
                    </Button>
                  </Box>
                </Box>
              </Box>
            </Paper>

            {/* Creator Section */}
            <Paper elevation={0} sx={{ p: 4 }}>
              <Box sx={{ textAlign: 'center' }}>
                <Box sx={{ mb: 3 }}>
                <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 700 }}>
                    Meet the Creator
                </Typography>
                  <Avatar 
                    src="https://yt3.googleusercontent.com/ytc/AIdro_l3n-1vpu1cTeDkAfINff0TgzedVxRQf25JSS8ebcVYEk4=s160-c-k-c0x00ffffff-no-rj"
                    sx={{ 
                      mx: 'auto',
                      mb: 2,
                      width: 80,
                      height: 80,
                      boxShadow: '0 10px 30px rgba(255, 0, 0, 0.3)',
                    }}
                  >
                    <YouTubeIcon sx={{ fontSize: 40 }} />
                  </Avatar>
                  <Typography variant="h6" component="h3" sx={{ mb: 1, color: 'primary.main' }}>
                    That Insane Guy
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Content Creator & AI Developer
                  </Typography>
                </Box>

                <Button
                  variant="contained"
                  startIcon={<YouTubeIcon />}
                  href="https://www.youtube.com/@ThatInsaneGuy"
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{
                    background: 'linear-gradient(135deg, #FF0000 0%, #CC0000 100%)',
                    color: 'white',
                    fontWeight: 600,
                    px: 4,
                    py: 1.5,
                    fontSize: '1rem',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #CC0000 0%, #990000 100%)',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 10px 20px rgba(255,0,0,0.3)',
                    },
                  }}
                >
                  Subscribe to our YouTube Channel
                </Button>
              </Box>
            </Paper>
          </Box>
        </Fade>
      </Container>
    </DashboardLayout>
  );
}; 