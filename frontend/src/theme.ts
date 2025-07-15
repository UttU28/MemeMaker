import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#6366f1',
      light: '#818cf8',
      dark: '#4f46e5',
    },
    secondary: {
      main: '#f59e0b',
      light: '#fbbf24',
      dark: '#d97706',
    },
    background: {
      default: '#0f172a',
      paper: '#1e293b',
    },
    text: {
      primary: '#f1f5f9',
      secondary: '#94a3b8',
    },
    success: {
      main: '#10b981',
      light: '#34d399',
      dark: '#059669',
    },
    error: {
      main: '#ef4444',
      light: '#f87171',
      dark: '#dc2626',
    },
    warning: {
      main: '#f59e0b',
      light: '#fbbf24',
      dark: '#d97706',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 800,
      fontSize: '3rem',
      letterSpacing: '-0.02em',
      background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      backgroundClip: 'text',
    },
    h2: {
      fontWeight: 700,
      fontSize: '2.25rem',
      letterSpacing: '-0.02em',
      color: '#f1f5f9',
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.5rem',
      letterSpacing: '-0.01em',
      color: '#f1f5f9',
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.25rem',
      letterSpacing: '-0.01em',
      color: '#f1f5f9',
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.125rem',
      letterSpacing: '-0.01em',
      color: '#f1f5f9',
    },
    h6: {
      fontWeight: 600,
      fontSize: '1rem',
      letterSpacing: '-0.01em',
      color: '#f1f5f9',
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.7,
      color: '#e2e8f0',
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.6,
      color: '#94a3b8',
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          background: `
            radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(120, 119, 198, 0.1) 0%, transparent 50%),
            linear-gradient(135deg, #0f172a 0%, #1e293b 100%)
          `,
          fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
        },
        // Global scrollbar styling
        '*': {
          // Webkit scrollbar styles (Chrome, Safari, Edge)
          '&::-webkit-scrollbar': {
            width: '8px',
            height: '8px',
          },
          '&::-webkit-scrollbar-track': {
            background: 'rgba(15, 23, 42, 0.5)',
            borderRadius: '8px',
          },
          '&::-webkit-scrollbar-thumb': {
            background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.6) 0%, rgba(139, 92, 246, 0.6) 100%)',
            borderRadius: '8px',
            border: '2px solid rgba(15, 23, 42, 0.3)',
            backdropFilter: 'blur(10px)',
            transition: 'all 0.3s ease',
          },
          '&::-webkit-scrollbar-thumb:hover': {
            background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.8) 0%, rgba(139, 92, 246, 0.8) 100%)',
            border: '2px solid rgba(99, 102, 241, 0.2)',
            transform: 'scale(1.1)',
          },
          '&::-webkit-scrollbar-thumb:active': {
            background: 'linear-gradient(135deg, rgba(99, 102, 241, 1) 0%, rgba(139, 92, 246, 1) 100%)',
          },
          '&::-webkit-scrollbar-corner': {
            background: 'rgba(15, 23, 42, 0.5)',
          },
        },
        // Firefox scrollbar styles
        html: {
          scrollbarWidth: 'thin',
          scrollbarColor: 'rgba(99, 102, 241, 0.6) rgba(15, 23, 42, 0.5)',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: 'rgba(15, 23, 42, 0.8)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(148, 163, 184, 0.1)',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: 'rgba(30, 41, 59, 0.8)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(148, 163, 184, 0.1)',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: 'rgba(30, 41, 59, 0.6)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(148, 163, 184, 0.1)',
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            backgroundColor: 'rgba(30, 41, 59, 0.8)',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
          padding: '12px 24px',
          fontSize: '0.875rem',
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
          },
        },
        contained: {
          background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
          color: 'white',
          '&:hover': {
            background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
          },
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          color: '#94a3b8',
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            color: '#6366f1',
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            transform: 'scale(1.1)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            backgroundColor: 'rgba(15, 23, 42, 0.5)',
            border: '1px solid rgba(148, 163, 184, 0.2)',
            borderRadius: 8,
            transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
            '&:hover': {
              border: '1px solid rgba(99, 102, 241, 0.5)',
            },
            '&.Mui-focused': {
              border: '1px solid #6366f1',
              boxShadow: '0 0 0 3px rgba(99, 102, 241, 0.1)',
            },
            '& fieldset': {
              border: 'none',
            },
          },
          '& .MuiInputLabel-root': {
            color: '#94a3b8',
            '&.Mui-focused': {
              color: '#6366f1',
            },
          },
          '& input': {
            color: '#f1f5f9',
            '&::placeholder': {
              color: '#94a3b8',
              opacity: 0.7,
            },
            '&:-webkit-autofill': {
              WebkitBoxShadow: '0 0 0 100px rgba(15, 23, 42, 0.8) inset !important',
              WebkitTextFillColor: '#f1f5f9 !important',
              borderRadius: '8px',
              transition: 'background-color 5000s ease-in-out 0s',
            },
            '&:-webkit-autofill:hover': {
              WebkitBoxShadow: '0 0 0 100px rgba(15, 23, 42, 0.8) inset !important',
              WebkitTextFillColor: '#f1f5f9 !important',
            },
            '&:-webkit-autofill:focus': {
              WebkitBoxShadow: '0 0 0 100px rgba(15, 23, 42, 0.8) inset !important',
              WebkitTextFillColor: '#f1f5f9 !important',
            },
            '&:-webkit-autofill:active': {
              WebkitBoxShadow: '0 0 0 100px rgba(15, 23, 42, 0.8) inset !important',
              WebkitTextFillColor: '#f1f5f9 !important',
            },
          },
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          fontWeight: 600,
          textTransform: 'none',
          fontSize: '1rem',
          color: '#94a3b8',
          '&.Mui-selected': {
            color: '#6366f1',
          },
        },
      },
    },
    MuiTabs: {
      styleOverrides: {
        root: {
          '& .MuiTabs-indicator': {
            height: 3,
            borderRadius: 2,
            background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
          },
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          '&.MuiAlert-standardError': {
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.2)',
            color: '#fca5a5',
            '& .MuiAlert-icon': {
              color: '#ef4444',
            },
          },
          '&.MuiAlert-standardSuccess': {
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            border: '1px solid rgba(16, 185, 129, 0.2)',
            color: '#6ee7b7',
            '& .MuiAlert-icon': {
              color: '#10b981',
            },
          },
          '&.MuiAlert-standardWarning': {
            backgroundColor: 'rgba(245, 158, 11, 0.1)',
            border: '1px solid rgba(245, 158, 11, 0.2)',
            color: '#fcd34d',
            '& .MuiAlert-icon': {
              color: '#f59e0b',
            },
          },
          '&.MuiAlert-standardInfo': {
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            border: '1px solid rgba(99, 102, 241, 0.2)',
            color: '#a5b4fc',
            '& .MuiAlert-icon': {
              color: '#6366f1',
            },
          },
        },
      },
    },
    MuiDivider: {
      styleOverrides: {
        root: {
          borderColor: 'rgba(148, 163, 184, 0.1)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 600,
          '& .MuiChip-label': {
            paddingLeft: 12,
            paddingRight: 12,
          },
        },
      },
    },

  },
});

export default theme; 