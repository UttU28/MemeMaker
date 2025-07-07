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
} from '@mui/material';
import {
  Warning as WarningIcon,
  Close as CloseIcon,
  Delete as DeleteIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

export interface ConfirmDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'delete' | 'warning' | 'info';
  loading?: boolean;
}

const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  open,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  variant = 'warning',
  loading = false,
}) => {
  const getVariantConfig = () => {
    switch (variant) {
      case 'delete':
        return {
          icon: <DeleteIcon sx={{ fontSize: 32 }} />,
          iconColor: '#ef4444',
          iconBg: 'rgba(239, 68, 68, 0.1)',
          confirmButtonColor: 'error.main',
          confirmButtonHover: 'rgba(239, 68, 68, 0.8)',
        };
      case 'warning':
        return {
          icon: <WarningIcon sx={{ fontSize: 32 }} />,
          iconColor: '#f59e0b',
          iconBg: 'rgba(245, 158, 11, 0.1)',
          confirmButtonColor: '#f59e0b',
          confirmButtonHover: 'rgba(245, 158, 11, 0.8)',
        };
      case 'info':
        return {
          icon: <InfoIcon sx={{ fontSize: 32 }} />,
          iconColor: '#3b82f6',
          iconBg: 'rgba(59, 130, 246, 0.1)',
          confirmButtonColor: 'primary.main',
          confirmButtonHover: 'rgba(99, 102, 241, 0.8)',
        };
    }
  };

  const config = getVariantConfig();

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
                background: config.iconBg,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: config.iconColor,
              }}
            >
              {config.icon}
            </Box>
            <Typography variant="h5" sx={{ fontWeight: 700, color: 'text.primary' }}>
              {title}
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
            mt: 1
          }}
        >
          {message}
        </Typography>
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
          {cancelText}
        </Button>
        <Button
          onClick={onConfirm}
          disabled={loading}
          sx={{
            px: 3,
            py: 1.5,
            fontWeight: 600,
            background: config.confirmButtonColor,
            color: 'white',
            '&:hover': {
              background: config.confirmButtonHover,
            },
            '&:disabled': {
              background: 'rgba(148, 163, 184, 0.3)',
              color: 'rgba(148, 163, 184, 0.5)',
            },
          }}
          variant="contained"
        >
          {loading ? 'Loading...' : confirmText}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ConfirmDialog; 