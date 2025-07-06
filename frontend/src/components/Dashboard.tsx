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
} from '@mui/material';
import {
  PhotoLibrary,
  TextFields,
  Download,
  Share,
  Create,
  Dashboard as DashboardIcon,
  PlayArrow,
  TrendingUp,
  Bolt,
  AutoAwesome,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const features = [
  {
    icon: <PhotoLibrary sx={{ fontSize: 40 }} />,
    title: 'Upload & Edit',
    description: 'Drag and drop images or browse from your device. Supports JPG, PNG, GIF, and WebP formats.',
    color: '#6366f1',
    gradient: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
  },
  {
    icon: <TextFields sx={{ fontSize: 40 }} />,
    title: 'Smart Text',
    description: 'Add dynamic text with custom fonts, colors, and effects. Auto-positioning for perfect placement.',
    color: '#f59e0b',
    gradient: 'linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)',
  },
  {
    icon: <AutoAwesome sx={{ fontSize: 40 }} />,
    title: 'AI Enhancement',
    description: 'Enhance your memes with AI-powered suggestions, filters, and automatic text placement.',
    color: '#10b981',
    gradient: 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)',
  },
  {
    icon: <Bolt sx={{ fontSize: 40 }} />,
    title: 'Quick Templates',
    description: 'Choose from hundreds of trending meme templates or create your own custom templates.',
    color: '#8b5cf6',
    gradient: 'linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)',
  },
  {
    icon: <Download sx={{ fontSize: 40 }} />,
    title: 'Export & Save',
    description: 'Download in high quality or save to cloud. Multiple formats and sizes available.',
    color: '#06b6d4',
    gradient: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
  },
  {
    icon: <Share sx={{ fontSize: 40 }} />,
    title: 'Share & Viral',
    description: 'Share directly to social media or get shareable links. Track your meme performance.',
    color: '#ef4444',
    gradient: 'linear-gradient(135deg, #ef4444 0%, #f97316 100%)',
  },
];

const Dashboard: React.FC = () => {
  const [hoveredCard, setHoveredCard] = useState<number | null>(null);
  const navigate = useNavigate();

  const handleStartCreating = () => {
    navigate('/auth');
  };

  return (
    <Box sx={{ minHeight: '100vh' }}>
      {/* Header */}
      <AppBar position="static" elevation={0}>
        <Toolbar>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Avatar
              sx={{
                mr: 2,
                background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                width: 40,
                height: 40,
              }}
            >
              <DashboardIcon />
            </Avatar>
            <Typography variant="h6" component="div" sx={{ fontWeight: 700 }}>
              Meme Maker
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
                mb: 3,
                color: 'text.secondary',
                maxWidth: 600,
                mx: 'auto',
                lineHeight: 1.6,
              }}
            >
              Transform your ideas into viral content with our AI-powered meme generator. 
              No design skills required.
            </Typography>
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              spacing={2}
              justifyContent="center"
              sx={{ mb: 4 }}
            >
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
                }}
              >
                Start Creating
              </Button>
              <Button
                variant="outlined"
                size="large"
                startIcon={<TrendingUp />}
                sx={{
                  px: 4,
                  py: 1.5,
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  borderColor: 'primary.main',
                  color: 'primary.main',
                  '&:hover': {
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    borderColor: 'primary.light',
                  },
                }}
              >
                View Templates
              </Button>
            </Stack>
            <Stack direction="row" spacing={3} justifyContent="center" sx={{ color: 'text.secondary' }}>
              <Typography variant="body2">
                <strong>10M+</strong> Memes Created
              </Typography>
              <Typography variant="body2">
                <strong>500+</strong> Templates
              </Typography>
              <Typography variant="body2">
                <strong>AI-Powered</strong> Editing
              </Typography>
            </Stack>
          </Box>
        </Fade>

        {/* Features Grid */}
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
            Everything You Need
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
            Powerful tools designed for creators, marketers, and meme enthusiasts
          </Typography>

          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: {
                xs: 'repeat(1, 1fr)',
                sm: 'repeat(2, 1fr)',
                md: 'repeat(3, 1fr)',
              },
              gap: 3,
            }}
          >
            {features.map((feature, index) => (
              <Zoom in timeout={500 + index * 100} key={index}>
                <Card
                  onMouseEnter={() => setHoveredCard(index)}
                  onMouseLeave={() => setHoveredCard(null)}
                  sx={{
                    height: '100%',
                    cursor: 'pointer',
                    position: 'relative',
                    overflow: 'hidden',
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: '4px',
                      background: feature.gradient,
                    },
                  }}
                >
                  <CardContent sx={{ p: 4, height: '100%' }}>
                    <Box
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        mb: 3,
                        color: feature.color,
                      }}
                    >
                      {feature.icon}
                      <Typography variant="h5" component="h3" sx={{ ml: 2, fontWeight: 600 }}>
                        {feature.title}
                      </Typography>
                    </Box>
                    <Typography variant="body1" sx={{ color: 'text.secondary', lineHeight: 1.7 }}>
                      {feature.description}
                    </Typography>
                    <Box
                      sx={{
                        mt: 3,
                        opacity: hoveredCard === index ? 1 : 0,
                        transform: hoveredCard === index ? 'translateY(0)' : 'translateY(10px)',
                        transition: 'all 0.3s ease',
                      }}
                    >
                      <Button
                        variant="text"
                        sx={{
                          color: feature.color,
                          fontWeight: 600,
                          '&:hover': {
                            backgroundColor: 'transparent',
                            color: feature.color,
                          },
                        }}
                      >
                        Learn More →
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Zoom>
            ))}
          </Box>
        </Box>

        {/* CTA Section */}
        <Fade in timeout={1500}>
          <Card
            sx={{
              background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%)',
              border: '1px solid rgba(99, 102, 241, 0.2)',
              textAlign: 'center',
              p: 6,
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            <Box
              sx={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                opacity: 0.05,
              }}
            />
            <Box sx={{ position: 'relative', zIndex: 1 }}>
              <Typography variant="h3" component="h2" gutterBottom sx={{ fontWeight: 700 }}>
                Ready to Go Viral?
              </Typography>
              <Typography variant="h6" sx={{ mb: 4, color: 'text.secondary', maxWidth: 600, mx: 'auto' }}>
                Join millions of creators who trust Meme Maker to bring their ideas to life.
                Start creating your first viral meme today!
              </Typography>
              <Button
                variant="contained"
                size="large"
                startIcon={<Create />}
                onClick={handleStartCreating}
                sx={{
                  px: 6,
                  py: 2,
                  fontSize: '1.2rem',
                  fontWeight: 600,
                  background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: '0 20px 40px rgba(99, 102, 241, 0.3)',
                  },
                }}
              >
                Start Creating Now
              </Button>
            </Box>
          </Card>
        </Fade>
      </Container>
    </Box>
  );
};

export default Dashboard; 