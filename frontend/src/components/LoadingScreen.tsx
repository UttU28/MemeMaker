import React from 'react';
import { Box, Typography, Fade } from '@mui/material';

interface LoadingScreenProps {
  message?: string;
}

export const LoadingScreen: React.FC<LoadingScreenProps> = ({ 
  message = 'Loading your dashboard...' 
}) => {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
      }}
    >
      {/* Background gradient overlay */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: `
            radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(120, 119, 198, 0.1) 0%, transparent 50%)
          `,
          opacity: 0.3,
        }}
      />

      <Fade in timeout={800}>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 4,
            position: 'relative',
            zIndex: 1,
          }}
        >
          {/* Animated logo */}
          <Box
            sx={{
              position: 'relative',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {/* Outer rotating ring */}
            <Box
              sx={{
                width: 80,
                height: 80,
                borderRadius: '50%',
                border: '2px solid transparent',
                background: 'linear-gradient(135deg, #6366f1, #8b5cf6) border-box',
                animation: 'rotate 3s linear infinite',
                position: 'absolute',
                '@keyframes rotate': {
                  '0%': { transform: 'rotate(0deg)' },
                  '100%': { transform: 'rotate(360deg)' },
                },
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  inset: 0,
                  padding: '2px',
                  background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                  borderRadius: '50%',
                  mask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
                  maskComposite: 'exclude',
                  WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
                  WebkitMaskComposite: 'xor',
                },
              }}
            />
            
            {/* Inner pulsing circle with Doofenshmirtz image */}
            <Box
              sx={{
                width: 60,
                height: 60,
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                animation: 'pulse 2s ease-in-out infinite',
                boxShadow: '0 0 30px rgba(99, 102, 241, 0.4)',
                '@keyframes pulse': {
                  '0%, 100%': { 
                    transform: 'scale(1)',
                    boxShadow: '0 0 30px rgba(99, 102, 241, 0.4)',
                  },
                  '50%': { 
                    transform: 'scale(1.05)',
                    boxShadow: '0 0 40px rgba(99, 102, 241, 0.6)',
                  },
                },
              }}
            >
              <Box
                component="img"
                src="/doofenshmirtz-flipped.png"
                alt="Dr. Doofenshmirtz"
                sx={{
                  width: 40,
                  height: 40,
                  borderRadius: '50%',
                  objectFit: 'cover',
                }}
              />
            </Box>
          </Box>

          {/* Loading text */}
          <Box sx={{ textAlign: 'center' }}>
            <Typography
              variant="h5"
              sx={{
                fontWeight: 600,
                mb: 2,
                background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              MemeVoiceClone-inator
            </Typography>
            <Typography 
              variant="body1" 
              sx={{ 
                color: 'text.secondary',
                animation: 'fadeInOut 2s ease-in-out infinite',
                '@keyframes fadeInOut': {
                  '0%, 100%': { opacity: 0.7 },
                  '50%': { opacity: 1 },
                },
              }}
            >
              {message}
            </Typography>
          </Box>

          {/* Decorative dots */}
          <Box sx={{ display: 'flex', gap: 1 }}>
            {[0, 1, 2].map((index) => (
              <Box
                key={index}
                sx={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                  animation: `bounce 1.4s ease-in-out ${index * 0.16}s infinite both`,
                  '@keyframes bounce': {
                    '0%, 80%, 100%': {
                      transform: 'scale(0)',
                      opacity: 0.5,
                    },
                    '40%': {
                      transform: 'scale(1)',
                      opacity: 1,
                    },
                  },
                }}
              />
            ))}
          </Box>
        </Box>
      </Fade>
    </Box>
  );
}; 