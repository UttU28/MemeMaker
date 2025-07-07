import React from 'react';
import {
  Box,
  Container,
  Typography,
  Avatar,
  Chip,
  Paper,
  Divider,
  Fade,
} from '@mui/material';
import {
  AccountCircle,
  Email,
  Verified,
  Star,
  Schedule
} from '@mui/icons-material';
import { useAuth } from '../../hooks/useAuth';

export const ProfileTab: React.FC = () => {
  const { user } = useAuth();

  if (!user) {
    return null;
  }


  const userInfo = [
    {
      icon: <Email sx={{ color: 'primary.main' }} />,
      title: 'Email',
      value: user.email,
      type: 'text' as const
    },
    {
      icon: <Verified sx={{ color: 'primary.main' }} />,
      title: 'Account Status',
      value: user.isVerified ? 'Verified' : 'Unverified',
      type: 'chip' as const,
      chipColor: (user.isVerified ? 'success' : 'warning') as 'success' | 'warning'
    },
    {
      icon: <Star sx={{ color: 'primary.main' }} />,
      title: 'Subscription',
      value: user.subscription || 'Free',
      type: 'chip' as const,
      chipColor: 'primary' as const
    },
    {
      icon: <Schedule sx={{ color: 'primary.main' }} />,
      title: 'Member Since',
      value: new Date(user.createdAt).toLocaleDateString(),
      type: 'text' as const
    }
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Welcome Section */}
      <Fade in timeout={800}>
        <Paper 
          elevation={0} 
          sx={{ 
            p: 4, 
            mb: 4, 
            borderRadius: 3,
            background: 'rgba(30, 41, 59, 0.8)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(148, 163, 184, 0.1)',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <Avatar 
              sx={{ 
                width: 80, 
                height: 80, 
                background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                mr: 3,
                boxShadow: '0 10px 15px -3px rgba(99, 102, 241, 0.3)',
              }}
            >
              <AccountCircle sx={{ fontSize: 50 }} />
            </Avatar>
            <Box>
              <Typography variant="h3" sx={{ fontWeight: 800, mb: 1 }}>
                Welcome back, {user.name}!
              </Typography>
              <Typography variant="h6" sx={{ color: 'text.secondary' }}>
                Ready to create some viral memes?
              </Typography>
            </Box>
          </Box>

          <Divider sx={{ my: 3, borderColor: 'rgba(148, 163, 184, 0.1)' }} />

          {/* User Info Grid - 2x2 Layout */}
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
              gap: 2,
            }}
          >
            {userInfo.map((info, index) => (
              <Box
                key={index}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  py: 1,
                }}
              >
                <Box sx={{ mr: 2 }}>
                  {info.icon}
                </Box>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="body1" sx={{ fontWeight: 600, color: 'text.primary', mb: 0.5 }}>
                    {info.title}
                  </Typography>
                  {info.type === 'chip' ? (
                    <Chip 
                      label={info.value} 
                      color={info.chipColor}
                      size="small"
                      sx={{
                        fontWeight: 600,
                        ...(info.chipColor === 'primary' && {
                          background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                        }),
                        '& .MuiChip-label': {
                          px: 2,
                        },
                      }}
                    />
                  ) : (
                    <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                      {info.value}
                    </Typography>
                  )}
                </Box>
              </Box>
            ))}
          </Box>
        </Paper>
      </Fade>
    </Container>
  );
}; 