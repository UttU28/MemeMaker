import React, { useState } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Tab,
  Tabs,
  Alert,
  CircularProgress,
  InputAdornment,
  IconButton,
  Divider,
  Fade,
} from '@mui/material';
import {
  Email as EmailIcon,
  Lock as LockIcon,
  Person as PersonIcon,
  Visibility,
  VisibilityOff,
} from '@mui/icons-material';
import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`auth-tabpanel-${index}`}
      aria-labelledby={`auth-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

export const Auth: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { login, signup } = useAuth();
  const navigate = useNavigate();

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
    setError('');
    setFormData({ name: '', email: '', password: '', confirmPassword: '' });
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const validateForm = () => {
    if (!formData.email || !formData.password) {
      setError('Please fill in all required fields');
      return false;
    }

    if (!validateEmail(formData.email)) {
      setError('Please enter a valid email address');
      return false;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      return false;
    }

    if (activeTab === 1) { // Signup
      if (!formData.name) {
        setError('Please enter your name');
        return false;
      }

      if (formData.password !== formData.confirmPassword) {
        setError('Passwords do not match');
        return false;
      }
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      if (activeTab === 0) { // Login
        await login({
          email: formData.email,
          password: formData.password,
        });
      } else { // Signup
        await signup({
          name: formData.name,
          email: formData.email,
          password: formData.password,
        });
      }

      // Redirect to dashboard on success
      navigate('/dashboard');
    } catch (error) {
      setError(error instanceof Error ? error.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: 2,
      }}
    >
      <Container maxWidth="sm">
        <Fade in timeout={800}>
          <Paper
            elevation={0}
            sx={{
              borderRadius: 4,
              overflow: 'hidden',
              backgroundColor: 'rgba(30, 41, 59, 0.9)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(148, 163, 184, 0.1)',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
            }}
          >
            <Box sx={{ p: 4 }}>
              <Typography
                variant="h3"
                align="center"
                sx={{
                  mb: 3,
                  fontWeight: 800,
                  background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                Meme Maker
              </Typography>

              <Tabs
                value={activeTab}
                onChange={handleTabChange}
                variant="fullWidth"
                sx={{ mb: 3 }}
              >
                <Tab label="Login" />
                <Tab label="Sign Up" />
              </Tabs>

              <Divider sx={{ mb: 3 }} />

              {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {error}
                </Alert>
              )}

              <form onSubmit={handleSubmit}>
                <TabPanel value={activeTab} index={0}>
                  {/* Login Form */}
                  <TextField
                    fullWidth
                    label="Email"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    margin="normal"
                    required
                    placeholder="Enter your email"
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <EmailIcon sx={{ color: 'text.secondary' }} />
                        </InputAdornment>
                      ),
                    }}
                  />

                  <TextField
                    fullWidth
                    label="Password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={handleInputChange}
                    margin="normal"
                    required
                    placeholder="Enter your password"
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <LockIcon sx={{ color: 'text.secondary' }} />
                        </InputAdornment>
                      ),
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton
                            onClick={() => setShowPassword(!showPassword)}
                            edge="end"
                            sx={{ color: 'text.secondary' }}
                          >
                            {showPassword ? <VisibilityOff /> : <Visibility />}
                          </IconButton>
                        </InputAdornment>
                      ),
                    }}
                  />
                </TabPanel>

                <TabPanel value={activeTab} index={1}>
                  {/* Signup Form */}
                  <TextField
                    fullWidth
                    label="Full Name"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    margin="normal"
                    required
                    placeholder="Enter your full name"
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <PersonIcon sx={{ color: 'text.secondary' }} />
                        </InputAdornment>
                      ),
                    }}
                  />

                  <TextField
                    fullWidth
                    label="Email"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    margin="normal"
                    required
                    placeholder="Enter your email"
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <EmailIcon sx={{ color: 'text.secondary' }} />
                        </InputAdornment>
                      ),
                    }}
                  />

                  <TextField
                    fullWidth
                    label="Password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={handleInputChange}
                    margin="normal"
                    required
                    placeholder="Create a password"
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <LockIcon sx={{ color: 'text.secondary' }} />
                        </InputAdornment>
                      ),
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton
                            onClick={() => setShowPassword(!showPassword)}
                            edge="end"
                            sx={{ color: 'text.secondary' }}
                          >
                            {showPassword ? <VisibilityOff /> : <Visibility />}
                          </IconButton>
                        </InputAdornment>
                      ),
                    }}
                  />

                  <TextField
                    fullWidth
                    label="Confirm Password"
                    name="confirmPassword"
                    type={showPassword ? 'text' : 'password'}
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    margin="normal"
                    required
                    placeholder="Confirm your password"
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <LockIcon sx={{ color: 'text.secondary' }} />
                        </InputAdornment>
                      ),
                    }}
                  />
                </TabPanel>

                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  size="large"
                  disabled={isLoading}
                  sx={{
                    mt: 4,
                    mb: 2,
                    py: 1.5,
                    fontSize: '1rem',
                    fontWeight: 600,
                    borderRadius: 2,
                    background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                    boxShadow: '0 10px 15px -3px rgba(99, 102, 241, 0.3)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
                      transform: 'translateY(-1px)',
                      boxShadow: '0 20px 25px -5px rgba(99, 102, 241, 0.4)',
                    },
                    '&:disabled': {
                      background: 'rgba(148, 163, 184, 0.3)',
                      color: 'rgba(148, 163, 184, 0.7)',
                    },
                  }}
                >
                  {isLoading ? (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <CircularProgress 
                        size={20} 
                        sx={{ 
                          color: 'rgba(255, 255, 255, 0.7)',
                          '& .MuiCircularProgress-circle': {
                            strokeLinecap: 'round',
                          },
                        }} 
                      />
                      <Typography variant="body2">
                        {activeTab === 0 ? 'Signing in...' : 'Creating account...'}
                      </Typography>
                    </Box>
                  ) : (
                    activeTab === 0 ? 'Sign In' : 'Create Account'
                  )}
                </Button>
              </form>

              <Box sx={{ textAlign: 'center', mt: 3 }}>
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                  {activeTab === 0 ? "Don't have an account? " : "Already have an account? "}
                  <Button
                    variant="text"
                    onClick={() => setActiveTab(activeTab === 0 ? 1 : 0)}
                    sx={{ 
                      textTransform: 'none', 
                      fontWeight: 600,
                      color: 'primary.main',
                      '&:hover': {
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                      },
                    }}
                  >
                    {activeTab === 0 ? 'Sign Up' : 'Sign In'}
                  </Button>
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Fade>
      </Container>
    </Box>
  );
}; 