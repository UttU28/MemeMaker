import React from 'react';
import {
  Box,
  Typography,
  Container,
  Paper,
  Avatar,
  Button,
  Fade,
  Zoom,
} from '@mui/material';
import {
  AutoAwesome as AutoAwesomeIcon,
  YouTube as YouTubeIcon,
  PersonAdd as PersonAddIcon,
  Create as CreateIcon,
  VideoLibrary as VideoLibraryIcon,
  Star as StarIcon,
  Whatshot as WhatshotIcon,
} from '@mui/icons-material';
import { DashboardLayout } from '../components/DashboardLayout';

export const AboutUsPage: React.FC = () => {
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
              <Typography 
                variant="h6" 
                color="text.secondary" 
                sx={{ 
                  maxWidth: 600, 
                  mx: 'auto',
                  lineHeight: 1.6,
                  opacity: 0.9,
                }}
              >
                Create viral memes in just 2 steps and get massive reach with AI-powered characters and scripts
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
                  <Avatar 
                    sx={{ 
                      mx: 'auto', 
                      mb: 3, 
                      width: 64, 
                      height: 64,
                      background: 'linear-gradient(135deg, #ff6b6b 0%, #feca57 100%)',
                      boxShadow: '0 10px 30px rgba(255, 107, 107, 0.3)',
                    }}
                  >
                    <WhatshotIcon sx={{ fontSize: 32 }} />
                  </Avatar>
                  <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 700 }}>
                    Why We Built This
                  </Typography>
                  <Typography variant="body1" color="text.secondary" sx={{ lineHeight: 1.7 }}>
                    This platform was built for fun! I saw all the memes getting viral and wanted in on the action. After creating the entire pipeline, I got bored... so now I'm showcasing it for everyone to use and create their own viral content! A revolutionary platform that lets you create viral memes in just 2 simple steps! Choose from AI-powered characters, generate engaging scripts automatically, and watch your content go viral. Get massive reach without any technical skills or expensive equipment.
                  </Typography>
                </Paper>
              </Zoom>
            </Box>

            {/* How to Use Section */}
            <Paper elevation={0} sx={{ p: 4, mb: 6 }}>
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

            {/* Creator Section */}
            <Paper elevation={0} sx={{ p: 4, mb: 6 }}>
              <Box sx={{ textAlign: 'center' }}>
                <Box sx={{ mb: 3 }}>
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
                  <Typography variant="h5" component="h2" sx={{ mb: 1, fontWeight: 700 }}>
                    Meet the Creator
                  </Typography>
                  <Typography variant="h6" component="h3" sx={{ mb: 1, color: 'primary.main' }}>
                    That Insane Guy
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Content Creator & AI Developer
                  </Typography>
                </Box>

                <Typography 
                  variant="body1" 
                  color="text.secondary" 
                  sx={{ 
                    maxWidth: 600, 
                    mx: 'auto',
                    mb: 3,
                    lineHeight: 1.7,
                    opacity: 0.9,
                  }}
                >
                  Created by That Insane Guy, a passionate developer and content creator who loves experimenting with AI technology and making it accessible to everyone. Follow the journey and get updates on new features!
                </Typography>
                
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
                    maxWidth: 700, 
                    mx: 'auto',
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
                    maxWidth: 700, 
                    mx: 'auto',
                    mb: 4,
                    lineHeight: 1.7,
                    opacity: 0.9,
                  }}
                >
                  This is pretty heavy on resources, so we'll probably be running for just a week and shutting it down if there's no interest. If you want in on this action or wanna keep using it, lemme know and I'll figure something out! Just comment down what you think and let's connect and build something good together.
                </Typography>

                <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
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
                      px: 3,
                      py: 1.5,
                      '&:hover': {
                        background: 'linear-gradient(135deg, #CC0000 0%, #990000 100%)',
                        transform: 'translateY(-2px)',
                      },
                    }}
                  >
                    Comment on YouTube
                  </Button>
                  
                  <Button
                    variant="outlined"
                    startIcon={<CreateIcon />}
                    sx={{
                      borderColor: 'primary.main',
                      color: 'primary.main',
                      fontWeight: 600,
                      px: 3,
                      py: 1.5,
                      '&:hover': {
                        borderColor: 'primary.light',
                        color: 'primary.light',
                        transform: 'translateY(-2px)',
                      },
                    }}
                  >
                    Let's Build Together
                  </Button>
                </Box>
              </Box>
            </Paper>

            {/* Why Choose Us Section */}
            <Paper elevation={0} sx={{ p: 4 }}>
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
                Why Choose Our Platform?
              </Typography>
              
              <Box sx={{ 
                display: 'grid', 
                gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr' }, 
                gap: 4 
              }}>
                {[
                  {
                    icon: <AutoAwesomeIcon sx={{ fontSize: 32 }} />,
                    title: 'AI-Powered',
                    description: 'Advanced AI models for natural script generation and high-quality voice cloning',
                    color: '#10b981',
                  },
                  {
                    icon: <StarIcon sx={{ fontSize: 32 }} />,
                    title: 'Easy to Use',
                    description: 'Simple 4-step process to create professional videos in minutes',
                    color: '#06b6d4',
                  },
                  {
                    icon: <VideoLibraryIcon sx={{ fontSize: 32 }} />,
                    title: 'Professional Quality',
                    description: 'Generate studio-quality videos with synchronized audio and visuals',
                    color: '#f59e0b',
                  },
                ].map((feature, index) => (
                  <Fade in timeout={1200 + index * 200} key={index}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Avatar 
                        sx={{ 
                          mx: 'auto', 
                          mb: 2, 
                          width: 64, 
                          height: 64,
                          background: `linear-gradient(135deg, ${feature.color} 0%, ${feature.color}CC 100%)`,
                          boxShadow: `0 10px 30px ${feature.color}40`,
                        }}
                      >
                        {feature.icon}
                      </Avatar>
                      <Typography variant="h6" sx={{ mb: 1.5, fontWeight: 600, color: feature.color }}>
                        {feature.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
                        {feature.description}
                      </Typography>
                    </Box>
                  </Fade>
                ))}
              </Box>
            </Paper>
          </Box>
        </Fade>
      </Container>
    </DashboardLayout>
  );
}; 