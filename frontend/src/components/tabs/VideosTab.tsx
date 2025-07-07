import React from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Fade,
  Button,
  Stack,
} from '@mui/material';
import {
  VideoLibrary as VideoIcon,
  Upload as UploadIcon,
  PlayCircleOutline as PlayIcon,
} from '@mui/icons-material';

export const VideosTab: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Fade in timeout={800}>
        <Box>
          {/* Header */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h3" sx={{ fontWeight: 800, mb: 2 }}>
              Videos
            </Typography>
            <Typography variant="h6" sx={{ color: 'text.secondary', mb: 4 }}>
              Your video library and projects
            </Typography>
          </Box>

          {/* Empty State */}
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
                background: 'linear-gradient(135deg, #10b981 0%, #f59e0b 100%)',
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
              No Videos Yet
            </Typography>
            
            <Typography variant="h6" sx={{ color: 'text.secondary', mb: 4, maxWidth: 500, mx: 'auto' }}>
              Upload and manage your video projects. Create AI-powered videos with your characters and scripts.
            </Typography>
            
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="center">
              <Button
                variant="contained"
                size="large"
                startIcon={<PlayIcon />}
                sx={{
                  px: 4,
                  py: 1.5,
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  borderRadius: 2,
                  background: 'linear-gradient(135deg, #10b981 0%, #f59e0b 100%)',
                  boxShadow: '0 10px 15px -3px rgba(16, 185, 129, 0.3)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #059669 0%, #d97706 100%)',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 20px 25px -5px rgba(16, 185, 129, 0.4)',
                  },
                }}
              >
                Create Video
              </Button>
              
              <Button
                variant="outlined"
                size="large"
                startIcon={<UploadIcon />}
                sx={{
                  px: 4,
                  py: 1.5,
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  borderRadius: 2,
                  borderColor: '#10b981',
                  color: '#10b981',
                  '&:hover': {
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderColor: '#34d399',
                    transform: 'translateY(-2px)',
                  },
                }}
              >
                Upload Video
              </Button>
            </Stack>
          </Paper>
        </Box>
      </Fade>
    </Container>
  );
}; 