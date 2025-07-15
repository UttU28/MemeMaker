import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Avatar,
  Button,
  Zoom,
} from '@mui/material';
import {
  Warning as WarningIcon,
  YouTube as YouTubeIcon,
  GitHub as GitHubIcon,
  LinkedIn as LinkedInIcon,
  Build as BuildIcon,
  Gavel as GavelIcon,
  Shield as ShieldIcon,
  Lightbulb as LightbulbIcon,
} from '@mui/icons-material';

export const ProjectShowcase: React.FC = () => {
  return (
    <Zoom in timeout={600}>
      <Paper 
        elevation={0}
        sx={{ 
          p: 4, 
          textAlign: 'center',
          width: '100%',
          mx: 'auto',
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '4px',
            background: 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)',
            },
          }}
        >
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            gap: 2, 
            mb: 4 
          }}>
            <LightbulbIcon sx={{ color: '#f59e0b', fontSize: '2rem' }} />
            <Typography 
              variant="h4" 
              component="h2" 
              sx={{ 
                fontWeight: 700,
                background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              Why I Built This
            </Typography>
          </Box>
          <Typography variant="body1" color="text.secondary" sx={{ lineHeight: 1.7, mb: 3 }}>
            This platform was built for fun! I saw all the memes getting viral and wanted in on the action. After creating the entire pipeline, I got bored... so now I'm showcasing it for everyone to use and create their own viral content! Get massive reach without any technical skills or expensive equipment.
          </Typography>
          
          <Typography variant="body1" color="text.secondary" sx={{ lineHeight: 1.7, mb: 2 }}>
            This is a demonstration of my technical skills in building a complete meme creation pipeline. The project showcases automated content generation, voice cloning integration with F5-TTS, video processing workflows, and scalable architecture for daily meme production and social media distribution. Built as a proof-of-concept to demonstrate full-stack development capabilities, AI integration, and content automation systems.
          </Typography>
          
          <Typography 
            variant="body2" 
            sx={{ 
              color: 'text.disabled',
              fontStyle: 'italic',
              textAlign: 'center',
            }}
          >
            Created to explore the intersection of AI, automation, and viral content creation.
          </Typography>
          
          {/* Signature Section */}
          <Box sx={{ 
            mt: 6, 
            pt: 4, 
            borderTop: '1px solid rgba(148, 163, 184, 0.1)',
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: 3,
          }}>
            {/* Creator Info */}
            <Box 
              component="a"
              href="https://www.youtube.com/@ThatInsaneGuy"
              target="_blank"
              rel="noopener noreferrer"
              sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: 2,
                textDecoration: 'none',
                color: 'inherit',
                borderRadius: '12px',
                px: 2,
                py: 1.5,
                transition: 'all 0.2s ease',
                cursor: 'pointer',
                '&:hover': {
                  backgroundColor: 'rgba(99, 102, 241, 0.05)',
                  transform: 'translateY(-1px)',
                },
              }}
            >
              <Avatar 
                src="/me.png"
                sx={{ 
                  width: 48,
                  height: 48,
                  border: '2px solid rgba(148, 163, 184, 0.2)',
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
                }}
              />
              <Box>
                <Typography variant="body1" sx={{ 
                  fontWeight: 600,
                  color: 'text.primary',
                }}>
                  Utsav Chaudhary
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <YouTubeIcon sx={{ color: '#FF0000', fontSize: 16 }} />
                  <Typography variant="body2" sx={{ 
                    color: 'text.secondary',
                    fontSize: '0.875rem',
                  }}>
                    @ThatInsaneGuy
                  </Typography>
                </Box>
              </Box>
            </Box>

            {/* Social Links */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography variant="body2" sx={{ 
                color: 'text.secondary',
                fontStyle: 'italic',
                display: { xs: 'none', sm: 'block' },
                fontSize: '0.875rem',
                fontWeight: 500,
              }}>
                Follow the journey
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<GitHubIcon />}
                  href="https://github.com/UttU28/"
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{
                    color: 'text.primary',
                    borderColor: 'rgba(148, 163, 184, 0.3)',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    px: 2,
                    py: 0.8,
                    borderRadius: '10px',
                    textTransform: 'none',
                    background: 'rgba(148, 163, 184, 0.02)',
                    minWidth: 'auto',
                    '&:hover': {
                      backgroundColor: 'rgba(148, 163, 184, 0.08)',
                      borderColor: 'text.primary',
                      transform: 'translateY(-1px)',
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
                    },
                    transition: 'all 0.3s ease',
                  }}
                >
                  GitHub
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<LinkedInIcon />}
                  href="https://www.linkedin.com/in/utsavmaan28/"
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{
                    color: '#0077B5',
                    borderColor: 'rgba(0, 119, 181, 0.3)',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    px: 2,
                    py: 0.8,
                    borderRadius: '10px',
                    textTransform: 'none',
                    background: 'rgba(0, 119, 181, 0.02)',
                    minWidth: 'auto',
                    '&:hover': {
                      backgroundColor: 'rgba(0, 119, 181, 0.08)',
                      borderColor: '#0077B5',
                      transform: 'translateY(-1px)',
                      boxShadow: '0 4px 12px rgba(0, 119, 181, 0.15)',
                    },
                    transition: 'all 0.3s ease',
                  }}
                >
                  LinkedIn
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<YouTubeIcon />}
                  href="https://www.youtube.com/@ThatInsaneGuy"
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{
                    color: '#FF0000',
                    borderColor: 'rgba(255, 0, 0, 0.3)',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    px: 2,
                    py: 0.8,
                    borderRadius: '10px',
                    textTransform: 'none',
                    background: 'rgba(255, 0, 0, 0.02)',
                    minWidth: 'auto',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 0, 0, 0.08)',
                      borderColor: '#FF0000',
                      transform: 'translateY(-1px)',
                      boxShadow: '0 4px 12px rgba(255, 0, 0, 0.15)',
                    },
                    transition: 'all 0.3s ease',
                  }}
                >
                  YouTube
                </Button>
              </Box>
            </Box>
          </Box>
          
          {/* Legal Disclaimer */}
          <Box sx={{ 
            mt: 4, 
            pt: 3, 
            borderTop: '1px solid rgba(148, 163, 184, 0.1)',
            textAlign: 'center',
            background: 'rgba(220, 38, 38, 0.05)',
            borderRadius: 2,
            px: 3,
            py: 2,
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1, mb: 2 }}>
              <ShieldIcon sx={{ color: '#dc2626', fontSize: '1.4rem' }} />
              <Typography variant="body1" sx={{ 
                color: '#dc2626', 
                fontWeight: 700,
                fontSize: '1rem',
              }}>
                Legal Disclaimer
              </Typography>
              <GavelIcon sx={{ color: '#dc2626', fontSize: '1.4rem' }} />
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 2, textAlign: 'left' }}>
              <BuildIcon sx={{ color: '#dc2626', fontSize: '1.2rem', mt: 0.2, flexShrink: 0 }} />
              <Typography variant="body2" sx={{ 
                color: 'text.secondary',
                lineHeight: 1.6,
                fontSize: '0.875rem',
              }}>
                <strong>Use at your own risk:</strong> This tool is provided "as-is" for educational and entertainment purposes. 
                I am simply providing the technology - you are responsible for how you use it.
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, textAlign: 'left' }}>
              <WarningIcon sx={{ color: '#dc2626', fontSize: '1.2rem', mt: 0.2, flexShrink: 0 }} />
              <Typography variant="body2" sx={{ 
                color: 'text.secondary',
                lineHeight: 1.6,
                fontSize: '0.875rem',
              }}>
                <strong>Content responsibility:</strong> Ensure your memes comply with platform guidelines and respect intellectual property. 
                Create responsibly and have fun!
              </Typography>
            </Box>
          </Box>
        </Paper>
      </Zoom>
  );
}; 