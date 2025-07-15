import React, { useState } from 'react';
import {
  Box,
  Typography,
  Container,
  Paper,
  Button,
  Fade,
  TextField,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Send as SendIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { DashboardLayout } from '../components/DashboardLayout';
import { feedbackAPI } from '../services/api';
import { useAuth } from '../hooks/useAuth';
import { ProjectShowcase } from '../components/ProjectShowcase';


export const AboutUsPage: React.FC = () => {
  const [userMessage, setUserMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<{
    type: 'success' | 'error' | null;
    message: string;
  }>({ type: null, message: '' });
  
  const { user } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!userMessage.trim()) return;
    
    setIsSubmitting(true);
    setSubmitStatus({ type: null, message: '' });
    
    try {
      console.log('Submitting user feedback:', {
        user: user?.name,
        email: user?.email,
        message: userMessage
      });
      
      const response = await feedbackAPI.submitFeedback(userMessage.trim());
      
      console.log('Feedback submission response:', response);
      
      if (response.success) {
        setSubmitStatus({
          type: 'success',
          message: response.message
        });
        setUserMessage(''); // Clear the input after successful submission
      } else {
        setSubmitStatus({
          type: 'error',
          message: response.message || 'Failed to submit feedback'
        });
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
      
      let errorMessage = 'Failed to submit feedback. Please try again.';
      
      if (error && typeof error === 'object') {
        if ('response' in error && error.response && typeof error.response === 'object' && 
            'data' in error.response && error.response.data && typeof error.response.data === 'object' &&
            'detail' in error.response.data) {
          errorMessage = String(error.response.data.detail);
        } else if ('message' in error && typeof error.message === 'string') {
          errorMessage = error.message;
        }
      }
      
      setSubmitStatus({
        type: 'error',
        message: errorMessage
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <DashboardLayout>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Fade in timeout={800}>
          <Box>
            {/* Header Section */}
            <Box sx={{ mb: 6 }}>
              <Typography 
                variant="h4" 
                component="h1" 
                sx={{ 
                  mb: 1,
                  color: 'white',
                  fontWeight: 700,
                }}
              >
                About Us
              </Typography>
              <Typography 
                variant="body1" 
                color="text.secondary" 
                sx={{ 
                  mb: 0,
                  opacity: 0.8,
                }}
              >
                Learn about the platform and connect with the creator
              </Typography>
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
                      disabled={!userMessage.trim() || isSubmitting}
                      startIcon={isSubmitting ? <CircularProgress size={24} color="inherit" /> : <SendIcon />}
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
                      {isSubmitting ? 'Sending...' : 'Send'}
                    </Button>
                  </Box>
                  {submitStatus.type && (
                    <Alert
                      severity={submitStatus.type}
                      sx={{ mt: 2 }}
                      icon={submitStatus.type === 'success' ? <CheckCircleIcon /> : undefined}
                    >
                      {submitStatus.message}
                    </Alert>
                  )}
                </Box>
              </Box>
            </Paper>

            {/* Why I Built This Section */}
            <Box sx={{ mt: 4 }}>
              <ProjectShowcase />
            </Box>

          </Box>
        </Fade>
      </Container>
    </DashboardLayout>
  );
}; 