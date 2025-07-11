import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  IconButton,
  Chip,
  Divider,
} from '@mui/material';
import {
  Close as CloseIcon,
  VideoFile as VideoFileIcon,
  PlaylistPlay,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { useAuth } from '../hooks/useAuth';

export interface VideoGenerationConfirmDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  scriptTitle: string;
  loading?: boolean;
  tokenCost?: number;
}

const VideoGenerationConfirmDialog: React.FC<VideoGenerationConfirmDialogProps> = ({
  open,
  onClose,
  onConfirm,
  scriptTitle,
  loading = false,
  tokenCost = 1,
}) => {
  const { user } = useAuth();
  const userTokens = user?.tokens || 0;
  const hasInsufficientTokens = userTokens < tokenCost;

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: '16px',
          background: 'rgba(30, 41, 59, 0.95)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(148, 163, 184, 0.1)',
        },
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box
              sx={{
                width: 48,
                height: 48,
                borderRadius: '12px',
                background: hasInsufficientTokens ? 'rgba(239, 68, 68, 0.1)' : 'rgba(59, 130, 246, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: hasInsufficientTokens ? '#ef4444' : '#3b82f6',
              }}
            >
              {hasInsufficientTokens ? (
                <WarningIcon sx={{ fontSize: 32 }} />
              ) : (
                <VideoFileIcon sx={{ fontSize: 32 }} />
              )}
            </Box>
            <Typography variant="h5" sx={{ fontWeight: 700, color: 'text.primary' }}>
              {hasInsufficientTokens ? 'Insufficient Tokens' : 'Generate Video'}
            </Typography>
          </Box>
          <IconButton
            onClick={onClose}
            disabled={loading}
            sx={{
              color: 'text.secondary',
              '&:hover': { 
                backgroundColor: 'rgba(148, 163, 184, 0.1)',
                color: 'text.primary'
              },
            }}
          >
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Typography 
          variant="body1" 
          sx={{ 
            color: 'text.secondary',
            lineHeight: 1.6,
            mb: 3
          }}
        >
          {hasInsufficientTokens 
            ? `You need ${tokenCost} token(s) to generate a video for "${scriptTitle}", but you only have ${userTokens} token(s).`
            : `Are you sure you want to generate a video for "${scriptTitle}"?`
          }
        </Typography>

        <Box sx={{ 
          background: 'rgba(148, 163, 184, 0.05)', 
          borderRadius: '12px', 
          p: 3,
          border: '1px solid rgba(148, 163, 184, 0.1)'
        }}>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, color: 'text.primary' }}>
            Token Information
          </Typography>
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
              Cost for video generation:
            </Typography>
            <Chip 
              label={`${tokenCost} token${tokenCost > 1 ? 's' : ''}`}
              color="warning"
              size="small"
              sx={{
                fontWeight: 600,
                background: 'linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)',
              }}
            />
          </Box>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
              Your current balance:
            </Typography>
            <Chip 
              icon={<PlaylistPlay />}
              label={`${userTokens} token${userTokens !== 1 ? 's' : ''}`}
              color={hasInsufficientTokens ? 'error' : 'success'}
              size="small"
              sx={{
                fontWeight: 600,
                ...(hasInsufficientTokens ? {
                  background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                } : {
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                }),
              }}
            />
          </Box>

          {!hasInsufficientTokens && (
            <>
              <Divider sx={{ my: 2, borderColor: 'rgba(148, 163, 184, 0.1)' }} />
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2" sx={{ color: 'text.secondary', fontWeight: 600 }}>
                  Balance after generation:
                </Typography>
                <Chip 
                  label={`${userTokens - tokenCost} token${(userTokens - tokenCost) !== 1 ? 's' : ''}`}
                  color="primary"
                  size="small"
                  sx={{
                    fontWeight: 600,
                    background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                  }}
                />
              </Box>
            </>
          )}
        </Box>

        {hasInsufficientTokens && (
          <Typography 
            variant="body2" 
            sx={{ 
              color: 'error.main',
              mt: 2,
              fontWeight: 500
            }}
          >
            Please contact support to purchase more tokens to continue generating videos.
          </Typography>
        )}
      </DialogContent>

      <DialogActions sx={{ p: 3, pt: 1 }}>
        <Button
          onClick={onClose}
          disabled={loading}
          sx={{
            px: 3,
            py: 1.5,
            fontWeight: 600,
            color: 'text.secondary',
            borderColor: 'rgba(148, 163, 184, 0.3)',
            '&:hover': {
              borderColor: 'text.primary',
              color: 'text.primary',
              backgroundColor: 'rgba(148, 163, 184, 0.1)',
            },
          }}
          variant="outlined"
        >
          Cancel
        </Button>
        {!hasInsufficientTokens && (
          <Button
            onClick={onConfirm}
            disabled={loading}
            sx={{
              px: 3,
              py: 1.5,
              fontWeight: 600,
              background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              color: 'white',
              '&:hover': {
                background: 'linear-gradient(135deg, #5b5bd6 0%, #7c3aed 100%)',
              },
              '&:disabled': {
                background: 'rgba(148, 163, 184, 0.3)',
                color: 'rgba(148, 163, 184, 0.5)',
              },
            }}
            variant="contained"
          >
            {loading ? 'Generating...' : 'Generate Video'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default VideoGenerationConfirmDialog; 