import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Fade,
  Button,
  Stack,
  Card,
  CardContent,
  CardMedia,
  Chip,
  IconButton,
  Skeleton,
  Alert,
  Tooltip,
  Tabs,
  Tab,
  TextField,
  Switch,
  Collapse,
  LinearProgress,
  Slider,
} from '@mui/material';
import {
  People as PeopleIcon,
  PersonAdd as PersonAddIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  Image as ImageIcon,
  NavigateBefore as PrevIcon,
  NavigateNext as NextIcon,
  FiberManualRecord as DotIcon,
  Speed as SpeedIcon,
  Settings as SettingsIcon,
  Close as CloseIcon,
  ExpandMore as ExpandMoreIcon,
  CloudUpload as UploadIcon,
  Delete as DeleteIcon,
  AudioFile as AudioIcon,
  Check as CheckIcon,
  Cancel as CancelIcon,
  Mic as MicIcon,
  Timer as TimerIcon,
  HighQuality as HighQualityIcon,
  AudioFile as AudioFormatIcon,
  PhotoLibrary as PhotoLibraryIcon,
  AutoFixHigh as AutoFixHighIcon,
} from '@mui/icons-material';
import { characterAPI, type Character, API_BASE_URL } from '../../services/api';
import ConfirmDialog from '../ConfirmDialog';

interface ImageCarouselProps {
  images: Record<string, string>;
  characterName: string;
}

const ImageCarousel: React.FC<ImageCarouselProps> = ({ images, characterName }) => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const imageArray = Object.entries(images);
  const totalImages = imageArray.length;

  const nextImage = () => {
    setCurrentImageIndex((prev) => (prev + 1) % totalImages);
  };

  const prevImage = () => {
    setCurrentImageIndex((prev) => (prev - 1 + totalImages) % totalImages);
  };

  const goToImage = (index: number) => {
    setCurrentImageIndex(index);
  };

  if (totalImages === 0) {
    return (
      <Box
        sx={{
          width: '100%',
          height: 200,
          background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderRadius: 2,
          mb: 2,
        }}
      >
        <ImageIcon sx={{ fontSize: 48, color: 'white', opacity: 0.7 }} />
      </Box>
    );
  }

  return (
    <Box sx={{ position: 'relative' }}>
      {/* Main Image */}
      <Box
        sx={{
          position: 'relative',
          width: '100%',
          height: 240,
          borderRadius: 2,
          overflow: 'hidden',
          mb: 1,
        }}
      >
        <CardMedia
          component="img"
          height="200"
          image={`${API_BASE_URL}${imageArray[currentImageIndex][1]}`}
          alt={`${characterName} - Image ${currentImageIndex + 1}`}
          sx={{
            objectFit: 'cover',
            transition: 'all 0.3s ease-in-out',
          }}
        />
        
        {/* Navigation Arrows - Only show if more than 1 image */}
        {totalImages > 1 && (
          <>
            <IconButton
              onClick={prevImage}
              disableRipple
              sx={{
                position: 'absolute',
                left: 8,
                top: '50%',
                transform: 'translateY(-50%)',
                backgroundColor: 'rgba(0, 0, 0, 0.5)',
                color: 'white',
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.5)',
                  transform: 'translateY(-50%)',
                },
              }}
              size="small"
            >
              <PrevIcon />
            </IconButton>
            <IconButton
              onClick={nextImage}
              disableRipple
              sx={{
                position: 'absolute',
                right: 8,
                top: '50%',
                transform: 'translateY(-50%)',
                backgroundColor: 'rgba(0, 0, 0, 0.5)',
                color: 'white',
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.5)',
                  transform: 'translateY(-50%)',
                },
              }}
              size="small"
            >
              <NextIcon />
            </IconButton>
            
            {/* Image Counter - Only show if more than 1 image */}
            <Box
              sx={{
                position: 'absolute',
                top: 8,
                right: 8,
                backgroundColor: 'rgba(0, 0, 0, 0.7)',
                color: 'white',
                px: 1.5,
                py: 0.5,
                borderRadius: 2,
                fontSize: '0.75rem',
                fontWeight: 600,
              }}
            >
              {currentImageIndex + 1} / {totalImages}
            </Box>
          </>
        )}
      </Box>

      {/* Dot Indicators - Always reserve space for consistent height */}
      <Box sx={{ display: 'flex', justifyContent: 'center', gap: 0.5, minHeight: 32 }}>
        {totalImages > 1 && imageArray.map((_, index) => (
          <IconButton
            key={index}
            onClick={() => goToImage(index)}
            size="small"
            sx={{ p: 0.5 }}
          >
            <DotIcon
              sx={{
                fontSize: 12,
                color: index === currentImageIndex ? 'primary.main' : 'text.secondary',
                transition: 'color 0.2s ease',
              }}
            />
          </IconButton>
        ))}
      </Box>
    </Box>
  );
};

interface CharacterCardProps {
  character: Character;
  onStarToggle: (characterId: string, isStarred: boolean) => Promise<void>;
  onDelete: (characterId: string) => Promise<void>;
  onUpdate: (characterId: string, updatedData: Partial<Character>) => void;
  activeTab: number;
  isEditing: boolean;
  onEditStart: (characterId: string) => void;
  onEditClose: (characterId: string) => void;
}

const CharacterCard: React.FC<CharacterCardProps> = ({ character, onStarToggle, onDelete, onUpdate, activeTab, isEditing, onEditStart, onEditClose }) => {
  const [isStarring, setIsStarring] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [editValues, setEditValues] = useState({
    speed: character.config.speed,
    nfeSteps: character.config.nfeSteps,
    crossFadeDuration: character.config.crossFadeDuration,
  });

  const handleStarToggle = async () => {
    setIsStarring(true);
    try {
      await onStarToggle(character.id, character.isStarred);
    } finally {
      setIsStarring(false);
    }
  };

  const handleDeleteClick = () => {
    setShowDeleteDialog(true);
  };

  const handleDeleteConfirm = async () => {
    setIsDeleting(true);
    try {
      await onDelete(character.id);
      setShowDeleteDialog(false);
    } catch (error) {
      console.error('Error deleting character:', error);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteDialog(false);
  };

  const handleEditClick = () => {
    onEditStart(character.id);
  };

  const handleEditCancel = () => {
    onEditClose(character.id);
    setEditValues({
      speed: character.config.speed,
      nfeSteps: character.config.nfeSteps,
      crossFadeDuration: character.config.crossFadeDuration,
    });
  };

  const handleEditValueChange = (field: string, value: number) => {
    setEditValues(prev => ({ ...prev, [field]: value }));
  };

  // Reset edit values when editing state changes
  useEffect(() => {
    if (!isEditing) {
      setEditValues({
        speed: character.config.speed,
        nfeSteps: character.config.nfeSteps,
        crossFadeDuration: character.config.crossFadeDuration,
      });
    }
  }, [isEditing, character.config]);

  const handleUpdateClick = async () => {
    setIsUpdating(true);
    try {
      const formData = new FormData();
      formData.append('speed', editValues.speed.toString());
      formData.append('nfeSteps', editValues.nfeSteps.toString());
      formData.append('crossFadeDuration', editValues.crossFadeDuration.toString());
      
      await characterAPI.updateCharacter(character.id, formData);
      
      // Update the character data dynamically
      onUpdate(character.id, {
        config: {
          ...character.config,
          speed: editValues.speed,
          nfeSteps: editValues.nfeSteps,
          crossFadeDuration: editValues.crossFadeDuration,
        }
      });
      
      onEditClose(character.id);
    } catch (error) {
      console.error('Error updating character:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <Fade in timeout={800}>
      <Card
        elevation={0}
        sx={{
          minHeight: 360,
          borderRadius: 3,
          background: 'rgba(30, 41, 59, 0.6)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(148, 163, 184, 0.1)',
          cursor: 'pointer',
          '&:hover': {
            border: '1px solid rgba(99, 102, 241, 0.3)',
          },
        }}
      >
        <CardContent sx={{ p: 2 }}>
          {/* Image Carousel */}
          <ImageCarousel images={character.images} characterName={character.displayName} />

          {/* Header with Name and Star/Actions */}
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1, mt: 1 }}>
            <Typography variant="h6" sx={{ fontWeight: 600, flex: 1 }}>
              {character.displayName}
            </Typography>
            
            {/* Show Edit/Delete for owned characters in My Characters tab, Star for non-owned characters */}
            {character.isOwner && activeTab === 0 ? (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                {!isEditing ? (
                  <>
                    <Tooltip title="Edit character">
                      <IconButton
                        onClick={handleEditClick}
                        size="small"
                        sx={{
                          color: 'primary.main',
                          '&:hover': {
                            backgroundColor: 'rgba(99, 102, 241, 0.1)',
                          },
                        }}
                      >
                        <SettingsIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete character">
                      <IconButton
                        onClick={handleDeleteClick}
                        disabled={isDeleting}
                        size="small"
                        sx={{
                          color: 'error.main',
                          '&:hover': {
                            backgroundColor: 'rgba(239, 68, 68, 0.1)',
                          },
                        }}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </>
                ) : (
                  <>
                    <Tooltip title="Save changes">
                      <IconButton
                        onClick={handleUpdateClick}
                        disabled={isUpdating}
                        size="small"
                        sx={{
                          color: '#22c55e',
                          '&:hover': {
                            backgroundColor: 'rgba(34, 197, 94, 0.1)',
                          },
                        }}
                      >
                        <CheckIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Cancel editing">
                      <IconButton
                        onClick={handleEditCancel}
                        disabled={isUpdating}
                        size="small"
                        sx={{
                          color: 'text.secondary',
                          '&:hover': {
                            backgroundColor: 'rgba(148, 163, 184, 0.1)',
                          },
                        }}
                      >
                        <CancelIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </>
                )}
              </Box>
            ) : !character.isOwner ? (
              <Tooltip title={character.isStarred ? 'Remove from favorites' : 'Add to favorites'}>
                <IconButton
                  onClick={handleStarToggle}
                  disabled={isStarring}
                  sx={{
                    color: character.isStarred ? '#f59e0b' : 'text.secondary',
                    '&:hover': {
                      color: '#f59e0b',
                      backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    },
                  }}
                >
                  {character.isStarred ? <StarIcon /> : <StarBorderIcon />}
                </IconButton>
              </Tooltip>
            ) : null}
          </Box>

          {/* Owner and Stats */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
            {character.isOwner ? (
              <Chip
                size="small"
                label="You"
                color="primary"
                sx={{
                  fontWeight: 600,
                  background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                }}
              />
            ) : character.createdByName ? (
              <Chip
                size="small"
                label={`by ${character.createdByName}`}
                sx={{
                  backgroundColor: 'rgba(148, 163, 184, 0.1)',
                  color: 'text.secondary',
                  fontWeight: 500,
                }}
              />
            ) : null}
            
            {character.starred > 0 && (
              <Chip
                size="small"
                icon={<StarIcon sx={{ fontSize: '14px !important' }} />}
                label={character.starred}
                sx={{
                  backgroundColor: 'rgba(245, 158, 11, 0.1)',
                  color: '#f59e0b',
                  fontWeight: 600,
                }}
              />
            )}

            <Chip
              size="small"
              icon={<SpeedIcon sx={{ fontSize: '14px !important', color: 'inherit' }} />}
              label={`${character.config.speed}x`}
              sx={{
                backgroundColor: 'rgba(34, 197, 94, 0.1)',
                color: '#22c55e',
                fontWeight: 600,
              }}
            />

            <Chip
              size="small"
              icon={<ImageIcon sx={{ fontSize: '14px !important', color: 'inherit' }} />}
              label={character.imageCount}
              sx={{
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                color: 'primary.main',
                fontWeight: 600,
              }}
            />
          </Box>

          {/* Character Info */}
          {isEditing && (
            <Box sx={{ 
              p: 1, 
              borderRadius: 1.5, 
              background: 'rgba(99, 102, 241, 0.08)', 
              border: '1px solid rgba(99, 102, 241, 0.15)',
              mt: 2
            }}>
              <Typography variant="body2" sx={{ fontWeight: 600, color: 'primary.main', fontSize: '0.8rem' }}>
                Edit Settings
              </Typography>
              
              {/* Speed Slider */}
              <Box>
                <Typography variant="body2" sx={{ color: 'text.secondary', mb: 0.2, fontSize: '0.75rem' }}>
                  Speed: {editValues.speed}x
                </Typography>
                <Slider
                  value={editValues.speed}
                  onChange={(_, value) => handleEditValueChange('speed', value as number)}
                  min={0.3}
                  max={2}
                  step={0.1}
                  size="small"
                  sx={{
                    height: 4,
                    '& .MuiSlider-thumb': {
                      backgroundColor: 'primary.main',
                      width: 16,
                      height: 16,
                    },
                    '& .MuiSlider-track': {
                      backgroundColor: 'primary.main',
                      height: 4,
                    },
                    '& .MuiSlider-rail': {
                      height: 4,
                    },
                  }}
                />
              </Box>

              {/* NFE Steps Slider */}
              <Box>
                <Typography variant="body2" sx={{ color: 'text.secondary', mb: 0.2, fontSize: '0.75rem' }}>
                  NFE Steps: {editValues.nfeSteps}
                </Typography>
                <Slider
                  value={editValues.nfeSteps}
                  onChange={(_, value) => handleEditValueChange('nfeSteps', value as number)}
                  min={4}
                  max={64}
                  step={1}
                  size="small"
                  sx={{
                    height: 4,
                    '& .MuiSlider-thumb': {
                      backgroundColor: 'primary.main',
                      width: 16,
                      height: 16,
                    },
                    '& .MuiSlider-track': {
                      backgroundColor: 'primary.main',
                      height: 4,
                    },
                    '& .MuiSlider-rail': {
                      height: 4,
                    },
                  }}
                />
              </Box>

              {/* Cross Fade Duration Slider */}
              <Box>
                <Typography variant="body2" sx={{ color: 'text.secondary', mb: 0.2, fontSize: '0.75rem' }}>
                  Cross Fade Duration: {editValues.crossFadeDuration}s
                </Typography>
                <Slider
                  value={editValues.crossFadeDuration}
                  onChange={(_, value) => handleEditValueChange('crossFadeDuration', value as number)}
                  min={0}
                  max={1}
                  step={0.05}
                  size="small"
                  sx={{
                    height: 4,
                    '& .MuiSlider-thumb': {
                      backgroundColor: 'primary.main',
                      width: 16,
                      height: 16,
                    },
                    '& .MuiSlider-track': {
                      backgroundColor: 'primary.main',
                      height: 4,
                    },
                    '& .MuiSlider-rail': {
                      height: 4,
                    },
                  }}
                />
              </Box>
            </Box>
          )}



          {/* Delete Confirmation Dialog */}
          <ConfirmDialog
            open={showDeleteDialog}
            onClose={handleDeleteCancel}
            onConfirm={handleDeleteConfirm}
            title="Delete Character"
            message={`Are you sure you want to delete "${character.displayName}"? This action cannot be undone.`}
            confirmText="Delete"
            cancelText="Cancel"
            variant="delete"
            loading={isDeleting}
          />
        </CardContent>
      </Card>
    </Fade>
  );
};

interface ImagePreview {
  file: File;
  preview: string;
  id: string;
}

interface CreateCharacterFormData {
  displayName: string;
  speed: number;
  nfeSteps: number;
  crossFadeDuration: number;
  removeSilences: boolean;
  audioFile: File | null;
  imageFiles: ImagePreview[];
}

const CreateCharacterForm: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}> = ({ isOpen, onClose, onSuccess }) => {
  const [formData, setFormData] = useState<CreateCharacterFormData>({
    displayName: '',
    speed: 1.0,
    nfeSteps: 32,
    crossFadeDuration: 0.15,
    removeSilences: true,
    audioFile: null,
    imageFiles: [],
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleInputChange = (field: keyof CreateCharacterFormData, value: string | number | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError(null);
  };

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    if (formData.imageFiles.length + files.length > 1) {
      setError('Maximum 1 image allowed per character');
      return;
    }

    // Validate that all files are PNG
    const nonPngFiles = files.filter(file => file.type !== 'image/png');
    if (nonPngFiles.length > 0) {
      setError('Only PNG format is accepted for transparency support');
      return;
    }

    const newImages: ImagePreview[] = files.map(file => ({
      file,
      preview: URL.createObjectURL(file),
      id: Math.random().toString(36).substr(2, 9),
    }));

    setFormData(prev => ({
      ...prev,
      imageFiles: [...prev.imageFiles, ...newImages],
    }));
  };

  const handleImageRemove = (id: string) => {
    setFormData(prev => ({
      ...prev,
      imageFiles: prev.imageFiles.filter(img => {
        if (img.id === id) {
          URL.revokeObjectURL(img.preview);
          return false;
        }
        return true;
      }),
    }));
  };

  const handleAudioUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate audio file
      const validAudioTypes = ['audio/wav', 'audio/mp3', 'audio/mpeg', 'audio/m4a', 'audio/flac', 'audio/ogg'];
      if (!validAudioTypes.includes(file.type)) {
        setError('Invalid audio file. Supported formats: WAV, MP3, M4A, FLAC, OGG');
        return;
      }
      if (file.size > 50 * 1024 * 1024) { // 50MB
        setError('Audio file too large. Maximum size: 50MB');
        return;
      }
      setFormData(prev => ({ ...prev, audioFile: file }));
      setError(null);
    }
  };

  const handleAudioRemove = () => {
    setFormData(prev => ({ ...prev, audioFile: null }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!formData.displayName.trim()) {
      setError('Character name is required');
      return;
    }
    if (!formData.audioFile) {
      setError('Audio file is required');
      return;
    }
    if (formData.imageFiles.length === 0) {
      setError('At least one image is required');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('displayName', formData.displayName.trim());
      formDataToSend.append('speed', formData.speed.toString());
      formDataToSend.append('nfeSteps', formData.nfeSteps.toString());
      formDataToSend.append('crossFadeDuration', formData.crossFadeDuration.toString());
      formDataToSend.append('removeSilences', formData.removeSilences.toString());
      formDataToSend.append('audioFile', formData.audioFile);
      
      formData.imageFiles.forEach(img => {
        formDataToSend.append('imageFiles', img.file);
      });

      await characterAPI.createCharacter(formDataToSend);
      
      // Clean up image previews
      formData.imageFiles.forEach(img => URL.revokeObjectURL(img.preview));
      
      onSuccess();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create character');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    // Clean up image previews
    formData.imageFiles.forEach(img => URL.revokeObjectURL(img.preview));
    setFormData({
      displayName: '',
      speed: 1.0,
      nfeSteps: 32,
      crossFadeDuration: 0.15,
      removeSilences: true,
      audioFile: null,
      imageFiles: [],
    });
    setError(null);
    onClose();
  };

  return (
    <Collapse in={isOpen} timeout={400}>
      <Paper
        elevation={0}
        sx={{
          mb: 4,
          borderRadius: 3,
          background: 'rgba(30, 41, 59, 0.8)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(99, 102, 241, 0.3)',
          overflow: 'hidden',
        }}
      >
        {loading && (
          <LinearProgress 
            sx={{ 
              height: 3,
              background: 'rgba(99, 102, 241, 0.1)',
              '& .MuiLinearProgress-bar': {
                background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              },
            }} 
          />
        )}
        
        <Box sx={{ p: 4 }}>
          {/* Header */}
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
            <Typography variant="h4" sx={{ fontWeight: 700, color: 'primary.main' }}>
              Create New Character
            </Typography>
            <IconButton 
              onClick={handleCancel}
              disabled={loading}
              sx={{ 
                color: 'text.secondary',
                '&:hover': { color: 'primary.main' },
              }}
            >
              <CloseIcon />
            </IconButton>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <Box sx={{ display: 'grid', gap: 4, gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' } }}>
              {/* Basic Information */}
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 3, color: 'text.primary' }}>
                  Basic Information
                </Typography>
                
                <TextField
                  fullWidth
                  label="Character Name"
                  value={formData.displayName}
                  onChange={(e) => handleInputChange('displayName', e.target.value)}
                  disabled={loading}
                  required
                  sx={{ mb: 3 }}
                  placeholder="Enter character name..."
                />

                {/* Character Images */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, color: 'text.primary' }}>
                    Character Images
                  </Typography>
                  
                                     {/* Image Helper Text */}
                   <Alert 
                     severity="info" 
                     sx={{ 
                       mb: 2, 
                       background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.05) 100%)',
                       border: '1px solid rgba(99, 102, 241, 0.3)',
                       borderRadius: '12px',
                       '& .MuiAlert-icon': { color: 'primary.main' },
                       '& .MuiAlert-message': { color: 'text.primary' }
                     }}
                   >
                     <Typography variant="body2" sx={{ fontWeight: 600, mb: 1.5, color: 'primary.main', display: 'flex', alignItems: 'center', gap: 1 }}>
                       <ImageIcon sx={{ fontSize: 18 }} />
                       Image Guidelines:
                     </Typography>
                     <Box sx={{ pl: 1 }}>
                       <Typography variant="body2" sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1.5 }}>
                         <Box sx={{ 
                           width: 24, 
                           height: 24, 
                           borderRadius: '50%', 
                           backgroundColor: 'rgba(99, 102, 241, 0.15)',
                           display: 'flex',
                           alignItems: 'center',
                           justifyContent: 'center'
                         }}>
                           <PhotoLibraryIcon sx={{ fontSize: 14, color: 'primary.main' }} />
                         </Box>
                         Use clear <strong>PNG images</strong> with transparent backgrounds
                       </Typography>
                       <Typography variant="body2" sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1.5 }}>
                         <Box sx={{ 
                           width: 24, 
                           height: 24, 
                           borderRadius: '50%', 
                           backgroundColor: 'rgba(139, 92, 246, 0.15)',
                           display: 'flex',
                           alignItems: 'center',
                           justifyContent: 'center'
                         }}>
                           <AutoFixHighIcon sx={{ fontSize: 14, color: '#8b5cf6' }} />
                         </Box>
                         For best results, use <strong>remove.bg</strong> to remove backgrounds
                       </Typography>
                       <Typography variant="body2" sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                         <Box sx={{ 
                           width: 24, 
                           height: 24, 
                           borderRadius: '50%', 
                           backgroundColor: 'rgba(34, 197, 94, 0.15)',
                           display: 'flex',
                           alignItems: 'center',
                           justifyContent: 'center'
                         }}>
                           <CheckIcon sx={{ fontSize: 14, color: '#22c55e' }} />
                         </Box>
                         Only <strong>PNG format</strong> is accepted for transparency support
                       </Typography>
                     </Box>
                   </Alert>
                  
                  <Box
                    component="label"
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 3,
                      p: 3,
                      cursor: formData.imageFiles.length >= 4 ? 'not-allowed' : 'pointer',
                      border: '2px dashed rgba(99, 102, 241, 0.4)',
                      borderRadius: '12px',
                      background: 'rgba(99, 102, 241, 0.03)',
                      opacity: formData.imageFiles.length >= 4 ? 0.5 : 1,
                      transition: 'all 0.3s ease',
                      mb: 3,
                      '&:hover': formData.imageFiles.length < 4 ? {
                        border: '2px dashed rgba(99, 102, 241, 0.6)',
                        background: 'rgba(99, 102, 241, 0.08)',
                        transform: 'translateY(-2px)',
                      } : {},
                    }}
                  >
                    <Box
                      sx={{
                        width: 48,
                        height: 48,
                        borderRadius: '50%',
                        background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                      }}
                    >
                      <ImageIcon sx={{ fontSize: 24, color: 'white' }} />
                    </Box>
                    <Box>
                      <Typography variant="body1" sx={{ fontWeight: 600, mb: 0.5, color: 'text.primary' }}>
                        Upload Image ({formData.imageFiles.length}/1)
                      </Typography>
                      <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                        PNG format only • Multiple files allowed
                      </Typography>
                    </Box>
                    <input
                      type="file"
                      accept="image/png"
                      multiple
                      onChange={handleImageUpload}
                      disabled={loading || formData.imageFiles.length >= 4}
                      style={{ display: 'none' }}
                    />
                  </Box>

                  {/* Image Previews */}
                  {formData.imageFiles.length > 0 && (
                    <Box sx={{ 
                      display: 'grid', 
                      gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))', 
                      gap: 2,
                      p: 3,
                      borderRadius: '12px',
                      background: 'rgba(30, 41, 59, 0.3)',
                      border: '1px solid rgba(148, 163, 184, 0.1)',
                    }}>
                      {formData.imageFiles.map((img) => (
                        <Box
                          key={img.id}
                          sx={{
                            position: 'relative',
                            aspectRatio: '1',
                            borderRadius: '8px',
                            overflow: 'hidden',
                            border: '2px solid rgba(99, 102, 241, 0.3)',
                            transition: 'all 0.2s ease',
                            '&:hover': {
                              border: '2px solid rgba(99, 102, 241, 0.5)',
                              transform: 'scale(1.05)',
                            },
                          }}
                        >
                          <img
                            src={img.preview}
                            alt="Preview"
                            style={{
                              width: '100%',
                              height: '100%',
                              objectFit: 'cover',
                            }}
                          />
                          <IconButton
                            onClick={() => handleImageRemove(img.id)}
                            disabled={loading}
                            sx={{
                              position: 'absolute',
                              top: 4,
                              right: 4,
                              backgroundColor: 'rgba(0, 0, 0, 0.8)',
                              color: 'white',
                              width: 28,
                              height: 28,
                              '&:hover': {
                                backgroundColor: 'rgba(239, 68, 68, 0.9)',
                                transform: 'scale(1.1)',
                              },
                            }}
                            size="small"
                          >
                            <DeleteIcon sx={{ fontSize: 16 }} />
                          </IconButton>
                        </Box>
                      ))}
                    </Box>
                  )}
                </Box>
              </Box>

              {/* File Uploads */}
              <Box>
                {/* Audio Upload Section */}
                <Box sx={{ mb: 4 }}>
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, color: 'text.primary' }}>
                    Audio File
                  </Typography>
                  
                                     {/* Audio Helper Text */}
                   <Alert 
                     severity="info" 
                     sx={{ 
                       mb: 2, 
                       background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.05) 100%)',
                       border: '1px solid rgba(99, 102, 241, 0.3)',
                       borderRadius: '12px',
                       '& .MuiAlert-icon': { color: 'primary.main' },
                       '& .MuiAlert-message': { color: 'text.primary' }
                     }}
                   >
                     <Typography variant="body2" sx={{ fontWeight: 600, mb: 1.5, color: 'primary.main', display: 'flex', alignItems: 'center', gap: 1 }}>
                       <MicIcon sx={{ fontSize: 18 }} />
                       Audio Guidelines:
                     </Typography>
                     <Box sx={{ pl: 1 }}>
                       <Typography variant="body2" sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1.5 }}>
                         <Box sx={{ 
                           width: 24, 
                           height: 24, 
                           borderRadius: '50%', 
                           backgroundColor: 'rgba(99, 102, 241, 0.15)',
                           display: 'flex',
                           alignItems: 'center',
                           justifyContent: 'center'
                         }}>
                           <TimerIcon sx={{ fontSize: 14, color: 'primary.main' }} />
                         </Box>
                         Use <strong>clear English speech</strong> around <strong>30 seconds</strong> duration
                       </Typography>
                       <Typography variant="body2" sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1.5 }}>
                         <Box sx={{ 
                           width: 24, 
                           height: 24, 
                           borderRadius: '50%', 
                           backgroundColor: 'rgba(139, 92, 246, 0.15)',
                           display: 'flex',
                           alignItems: 'center',
                           justifyContent: 'center'
                         }}>
                           <HighQualityIcon sx={{ fontSize: 14, color: '#8b5cf6' }} />
                         </Box>
                         High-quality audio with minimal background noise
                       </Typography>
                       <Typography variant="body2" sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                         <Box sx={{ 
                           width: 24, 
                           height: 24, 
                           borderRadius: '50%', 
                           backgroundColor: 'rgba(34, 197, 94, 0.15)',
                           display: 'flex',
                           alignItems: 'center',
                           justifyContent: 'center'
                         }}>
                           <AudioFormatIcon sx={{ fontSize: 14, color: '#22c55e' }} />
                         </Box>
                         Supported formats: WAV, MP3, M4A, FLAC, OGG (Max: 50MB)
                       </Typography>
                     </Box>
                   </Alert>

                  {!formData.audioFile ? (
                    <Box
                      component="label"
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 3,
                        p: 3,
                        cursor: 'pointer',
                        border: '2px dashed rgba(99, 102, 241, 0.4)',
                        borderRadius: '12px',
                        background: 'rgba(99, 102, 241, 0.03)',
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          border: '2px dashed rgba(99, 102, 241, 0.6)',
                          background: 'rgba(99, 102, 241, 0.08)',
                          transform: 'translateY(-2px)',
                        },
                      }}
                    >
                      <Box
                        sx={{
                          width: 48,
                          height: 48,
                          borderRadius: '50%',
                          background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          flexShrink: 0,
                        }}
                      >
                        <UploadIcon sx={{ fontSize: 24, color: 'white' }} />
                      </Box>
                      <Box>
                        <Typography variant="body1" sx={{ fontWeight: 600, mb: 0.5, color: 'text.primary' }}>
                          Click to upload audio file
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                          WAV, MP3, M4A, FLAC, OGG • Maximum size: 50MB
                        </Typography>
                      </Box>
                      <input
                        type="file"
                        accept="audio/*"
                        onChange={handleAudioUpload}
                        disabled={loading}
                        style={{ display: 'none' }}
                      />
                    </Box>
                  ) : (
                    <Box
                      sx={{
                        p: 3,
                        borderRadius: '12px',
                        background: 'rgba(34, 197, 94, 0.08)',
                        border: '1px solid rgba(34, 197, 94, 0.3)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 2,
                      }}
                    >
                      <Box
                        sx={{
                          width: 48,
                          height: 48,
                          borderRadius: '8px',
                          background: 'rgba(34, 197, 94, 0.2)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                        }}
                      >
                        <AudioIcon sx={{ fontSize: 24, color: 'success.main' }} />
                      </Box>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="body1" sx={{ fontWeight: 600, color: 'text.primary' }}>
                          {formData.audioFile.name}
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                          {(formData.audioFile.size / (1024 * 1024)).toFixed(2)} MB
                        </Typography>
                      </Box>
                      <IconButton 
                        onClick={handleAudioRemove} 
                        disabled={loading}
                        sx={{ 
                          color: 'error.main',
                          '&:hover': { backgroundColor: 'rgba(239, 68, 68, 0.1)' }
                        }}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  )}
                </Box>

                {/* Advanced Configuration */}
                <Box sx={{ mb: 3 }}>
                  <Box
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      p: 2.5,
                      cursor: 'pointer',
                      borderRadius: '12px',
                      background: 'rgba(30, 41, 59, 0.3)',
                      border: '1px solid rgba(148, 163, 184, 0.1)',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        background: 'rgba(30, 41, 59, 0.5)',
                        border: '1px solid rgba(99, 102, 241, 0.3)',
                      },
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Box
                        sx={{
                          width: 40,
                          height: 40,
                          borderRadius: '8px',
                          background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                        }}
                      >
                        <SettingsIcon sx={{ fontSize: 20, color: 'white' }} />
                      </Box>
                      <Box>
                        <Typography variant="h6" sx={{ fontWeight: 600, color: 'text.primary', mb: 0.5 }}>
                          Advanced Configuration
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                          {showAdvanced ? 'Hide advanced settings' : 'Click to configure voice settings'}
                        </Typography>
                      </Box>
                    </Box>
                    <IconButton
                      disableRipple
                      sx={{
                        color: 'text.secondary',
                        transform: showAdvanced ? 'rotate(180deg)' : 'rotate(0deg)',
                        transition: 'transform 0.3s ease',
                        '&:hover': {
                          backgroundColor: 'rgba(99, 102, 241, 0.1)',
                          color: 'primary.main',
                        },
                      }}
                    >
                      <ExpandMoreIcon />
                    </IconButton>
                  </Box>

                  <Collapse in={showAdvanced} timeout={400}>
                    <Box sx={{ 
                      display: 'grid', 
                      gap: 3, 
                      gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, 
                      mt: 2,
                      p: 3,
                      borderRadius: '12px',
                      background: 'rgba(30, 41, 59, 0.2)',
                      border: '1px solid rgba(148, 163, 184, 0.1)',
                    }}>
                      <Box>
                        <Typography variant="body2" sx={{ mb: 1, color: 'text.secondary', fontWeight: 500 }}>
                          Speed: {formData.speed}
                        </Typography>
                        <Slider
                          value={formData.speed}
                          onChange={(_, value) => handleInputChange('speed', value as number)}
                          min={0.3}
                          max={2.0}
                          step={0.1}
                          disabled={loading}
                          sx={{
                            color: 'primary.main',
                            '& .MuiSlider-thumb': {
                              backgroundColor: 'primary.main',
                              width: 20,
                              height: 20,
                            },
                            '& .MuiSlider-track': {
                              backgroundColor: 'primary.main',
                            },
                            '& .MuiSlider-rail': {
                              backgroundColor: 'rgba(148, 163, 184, 0.3)',
                            },
                          }}
                        />
                      </Box>
                      
                      <Box>
                        <Typography variant="body2" sx={{ mb: 1, color: 'text.secondary', fontWeight: 500 }}>
                          NFE Steps: {formData.nfeSteps}
                        </Typography>
                        <Slider
                          value={formData.nfeSteps}
                          onChange={(_, value) => handleInputChange('nfeSteps', value as number)}
                          min={4}
                          max={64}
                          step={1}
                          disabled={loading}
                          sx={{
                            color: 'primary.main',
                            '& .MuiSlider-thumb': {
                              backgroundColor: 'primary.main',
                              width: 20,
                              height: 20,
                            },
                            '& .MuiSlider-track': {
                              backgroundColor: 'primary.main',
                            },
                            '& .MuiSlider-rail': {
                              backgroundColor: 'rgba(148, 163, 184, 0.3)',
                            },
                          }}
                        />
                      </Box>
                      
                      <Box>
                        <Typography variant="body2" sx={{ mb: 1, color: 'text.secondary', fontWeight: 500 }}>
                          Cross Fade Duration: {formData.crossFadeDuration}
                        </Typography>
                        <Slider
                          value={formData.crossFadeDuration}
                          onChange={(_, value) => handleInputChange('crossFadeDuration', value as number)}
                          min={0.0}
                          max={1.0}
                          step={0.01}
                          disabled={loading}
                          sx={{
                            color: 'primary.main',
                            '& .MuiSlider-thumb': {
                              backgroundColor: 'primary.main',
                              width: 20,
                              height: 20,
                            },
                            '& .MuiSlider-track': {
                              backgroundColor: 'primary.main',
                            },
                            '& .MuiSlider-rail': {
                              backgroundColor: 'rgba(148, 163, 184, 0.3)',
                            },
                          }}
                        />
                      </Box>
                      
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Box>
                          <Typography variant="body2" sx={{ color: 'text.primary', fontWeight: 500, mb: 0.5 }}>
                            Remove Silences
                          </Typography>
                          <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                            {formData.removeSilences ? 'Enabled' : 'Disabled'}
                          </Typography>
                        </Box>
                        <Switch
                          checked={formData.removeSilences}
                          onChange={(e) => handleInputChange('removeSilences', e.target.checked)}
                          disabled={loading}
                          sx={{
                            '& .MuiSwitch-switchBase.Mui-checked': {
                              color: 'primary.main',
                            },
                            '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                              backgroundColor: 'primary.main',
                            },
                            '& .MuiSwitch-track': {
                              backgroundColor: 'rgba(148, 163, 184, 0.3)',
                            },
                            '& .MuiSwitch-thumb': {
                              width: 20,
                              height: 20,
                            },
                          }}
                        />
                      </Box>
                    </Box>
                  </Collapse>
                </Box>
              </Box>
            </Box>

            {/* Action Buttons */}
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mt: 4 }}>
              <Button
                variant="outlined"
                onClick={handleCancel}
                disabled={loading}
                startIcon={<CancelIcon />}
                sx={{
                  px: 3,
                  py: 1.5,
                  fontWeight: 600,
                  borderColor: 'text.secondary',
                  color: 'text.secondary',
                  '&:hover': {
                    borderColor: 'primary.main',
                    color: 'primary.main',
                  },
                }}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="contained"
                disabled={loading || !formData.displayName.trim() || !formData.audioFile || formData.imageFiles.length === 0}
                startIcon={loading ? null : <CheckIcon />}
                sx={{
                  px: 4,
                  py: 1.5,
                  fontWeight: 600,
                  background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
                  },
                  '&:disabled': {
                    background: 'rgba(148, 163, 184, 0.3)',
                  },
                }}
              >
                {loading ? 'Creating...' : 'Create Character'}
              </Button>
            </Box>
          </form>
        </Box>
      </Paper>
    </Collapse>
  );
};

export const CharactersTab: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [allCharacters, setAllCharacters] = useState<Character[]>([]);
  const [myCharacters, setMyCharacters] = useState<Character[]>([]);
  const [myFavorites, setMyFavorites] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingCharacterId, setEditingCharacterId] = useState<string | null>(null);

  const fetchAllCharacters = async () => {
    try {
      const data = await characterAPI.getAllCharacters();
      setAllCharacters(data);
    } catch (err) {
      console.error('Error fetching all characters:', err);
      throw err;
    }
  };

  const fetchMyCharacters = async () => {
    try {
      const data = await characterAPI.getMyCharacters();
      setMyCharacters(data);
    } catch (err) {
      console.error('Error fetching my characters:', err);
      throw err;
    }
  };

  const fetchMyFavorites = async () => {
    try {
      const data = await characterAPI.getMyFavorites();
      setMyFavorites(data);
    } catch (err) {
      console.error('Error fetching my favorites:', err);
      throw err;
    }
  };

  const fetchCharacters = async () => {
    try {
      setLoading(true);
      setError(null);
      await Promise.all([
        fetchAllCharacters(),
        fetchMyCharacters(),
        fetchMyFavorites(),
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch characters');
      console.error('Error fetching characters:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStarToggle = async (characterId: string, isCurrentlyStarred: boolean) => {
    try {
      setEditingCharacterId(null); // Close any open editing when starring/unstarring
      
      if (isCurrentlyStarred) {
        await characterAPI.unstarCharacter(characterId);
      } else {
        await characterAPI.starCharacter(characterId);
      }
      
      // Update the character in all relevant state arrays
      const updateCharacter = (char: Character) => char.id === characterId 
        ? { 
            ...char, 
            isStarred: !isCurrentlyStarred,
            starred: isCurrentlyStarred ? char.starred - 1 : char.starred + 1
          }
        : char;

      setAllCharacters(prev => prev.map(updateCharacter));
      setMyCharacters(prev => prev.map(updateCharacter));
      setMyFavorites(prev => prev.map(updateCharacter));
    } catch (err) {
      console.error('Error toggling star:', err);
    }
  };

  const handleDelete = async (characterId: string) => {
    try {
      setEditingCharacterId(null); // Close any open editing when deleting
      
      await characterAPI.deleteCharacter(characterId);
      
      // Remove the character from all state arrays
      const removeCharacter = (chars: Character[]) => chars.filter(char => char.id !== characterId);
      
      setAllCharacters(removeCharacter);
      setMyCharacters(removeCharacter);
      setMyFavorites(removeCharacter);
    } catch (err) {
      console.error('Error deleting character:', err);
      throw err; // Re-throw to handle in the card component
    }
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setEditingCharacterId(null); // Close any open editing when changing tabs
    setActiveTab(newValue);
  };

  const handleEditStart = (characterId: string) => {
    setEditingCharacterId(characterId);
  };

  const handleEditClose = (characterId: string) => {
    if (editingCharacterId === characterId) {
      setEditingCharacterId(null);
    }
  };

  const handleUpdate = (characterId: string, updatedData: Partial<Character>) => {
    // Update the character in all relevant state arrays
    const updateCharacter = (char: Character) => char.id === characterId 
      ? { ...char, ...updatedData }
      : char;

    setAllCharacters(prev => prev.map(updateCharacter));
    setMyCharacters(prev => prev.map(updateCharacter));
    setMyFavorites(prev => prev.map(updateCharacter));
  };

  // Get the current characters to display based on active tab
  const getCurrentCharacters = () => {
    if (activeTab === 0) {
      // My Characters: combine owned characters and favorites
      const ownedCharacters = myCharacters;
      const favoriteCharacters = myFavorites.filter(fav => 
        !ownedCharacters.some(owned => owned.id === fav.id)
      );
      return [...ownedCharacters, ...favoriteCharacters];
    } else {
      // All Characters
      return allCharacters;
    }
  };

  const currentCharacters = getCurrentCharacters();

  const handleCreateCharacterClick = () => {
    setEditingCharacterId(null); // Close any open editing when creating a character
    setShowCreateForm(true);
  };

  const handleFormClose = () => {
    setShowCreateForm(false);
  };

  const handleFormSuccess = () => {
    fetchCharacters();
    // Switch to "My Characters" tab to show the newly created character
    setActiveTab(0);
  };

  useEffect(() => {
    fetchCharacters();
  }, []);

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ mb: 4 }}>
          <Typography variant="h3" sx={{ fontWeight: 800, mb: 2 }}>
            Characters
          </Typography>
          <Typography variant="h6" sx={{ color: 'text.secondary', mb: 4 }}>
            Manage your AI characters for content creation
          </Typography>
          
          {/* Tab Navigation */}
          <Tabs 
            value={activeTab} 
            onChange={handleTabChange}
            sx={{
              '& .MuiTabs-indicator': {
                background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              },
              '& .MuiTab-root': {
                color: 'text.secondary',
                fontWeight: 600,
                fontSize: '1rem',
                textTransform: 'none',
                '&.Mui-selected': {
                  color: 'primary.main',
                },
              },
            }}
          >
            <Tab label="My Characters" />
            <Tab label="All Characters" />
          </Tabs>
        </Box>
        
        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 3 }}>
          {Array.from({ length: 3 }).map((_, idx) => (
            <Card
              key={idx}
              elevation={0}
              sx={{
                minHeight: 360,
                borderRadius: 3,
                background: 'rgba(30, 41, 59, 0.6)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(148, 163, 184, 0.1)',
              }}
            >
              <CardContent sx={{ p: 2 }}>
                {/* Image Carousel Skeleton */}
                <Box sx={{ position: 'relative', mb: 2 }}>
                  <Skeleton 
                    variant="rectangular" 
                    width="100%" 
                    height={240} 
                    sx={{ borderRadius: 2, mb: 1 }} 
                  />
                  {/* Dot indicators placeholder */}
                  <Box sx={{ display: 'flex', justifyContent: 'center', gap: 0.5, minHeight: 32 }}>
                    <Skeleton variant="circular" width={12} height={12} />
                    <Skeleton variant="circular" width={12} height={12} />
                    <Skeleton variant="circular" width={12} height={12} />
                  </Box>
                </Box>

                {/* Header with Name and Action Buttons */}
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1, mt: 1 }}>
                  <Skeleton variant="text" width="70%" height={24} />
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <Skeleton variant="circular" width={32} height={32} />
                    <Skeleton variant="circular" width={32} height={32} />
                  </Box>
                </Box>

                {/* Owner and Stats Chips */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                  <Skeleton variant="rounded" width={50} height={24} sx={{ borderRadius: 2 }} />
                  <Skeleton variant="rounded" width={40} height={24} sx={{ borderRadius: 2 }} />
                  <Skeleton variant="rounded" width={35} height={24} sx={{ borderRadius: 2 }} />
                  <Skeleton variant="rounded" width={30} height={24} sx={{ borderRadius: 2 }} />
                </Box>
              </CardContent>
            </Card>
          ))}
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert 
          severity="error" 
          sx={{ mb: 4 }}
          action={
            <Button color="inherit" size="small" onClick={fetchCharacters}>
              Retry
            </Button>
          }
        >
          {error}
        </Alert>
      </Container>
    );
  }

  if (currentCharacters.length === 0) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
              <Fade in timeout={800}>
        <Box>
          {/* Header */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h3" sx={{ fontWeight: 800, mb: 2 }}>
              Characters
            </Typography>
            <Typography variant="h6" sx={{ color: 'text.secondary', mb: 4 }}>
              Manage your AI characters for content creation
            </Typography>
            
            {/* Create Character Form */}
            <CreateCharacterForm
              isOpen={showCreateForm}
              onClose={handleFormClose}
              onSuccess={handleFormSuccess}
            />
            
            {/* Tab Navigation */}
            <Tabs 
              value={activeTab} 
              onChange={handleTabChange}
              sx={{
                '& .MuiTabs-indicator': {
                  background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                },
                '& .MuiTab-root': {
                  color: 'text.secondary',
                  fontWeight: 600,
                  fontSize: '1rem',
                  textTransform: 'none',
                  '&.Mui-selected': {
                    color: 'primary.main',
                  },
                },
              }}
            >
              <Tab label="My Characters" />
              <Tab label="All Characters" />
            </Tabs>
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
                  background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mx: 'auto',
                  mb: 3,
                  opacity: 0.8,
                }}
              >
                <PeopleIcon sx={{ fontSize: 60, color: 'white' }} />
              </Box>
              
              <Typography variant="h4" sx={{ fontWeight: 700, mb: 2 }}>
                {activeTab === 0 ? 'No Characters Yet' : 'No Characters Available'}
              </Typography>
              
              <Typography variant="h6" sx={{ color: 'text.secondary', mb: 4, maxWidth: 500, mx: 'auto' }}>
                {activeTab === 0 
                  ? 'Please create a new character to add characters or add some characters to favorite in order to show things here. You can check the other tab for other characters created by other people.'
                  : 'No characters have been created yet. Be the first to create a character!'
                }
              </Typography>
              
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="center">
                <Button
                  variant="contained"
                  size="large"
                  startIcon={<PersonAddIcon />}
                  onClick={handleCreateCharacterClick}
                  sx={{
                    px: 4,
                    py: 1.5,
                    fontSize: '1.1rem',
                    fontWeight: 600,
                    borderRadius: 2,
                    background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                    boxShadow: '0 10px 15px -3px rgba(99, 102, 241, 0.3)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 20px 25px -5px rgba(99, 102, 241, 0.4)',
                    },
                  }}
                >
                  Create Character
                </Button>
                
                {activeTab === 0 && (
                  <Button
                    variant="outlined"
                    size="large"
                    startIcon={<PeopleIcon />}
                    onClick={() => setActiveTab(1)}
                    sx={{
                      px: 4,
                      py: 1.5,
                      fontSize: '1.1rem',
                      fontWeight: 600,
                      borderRadius: 2,
                      borderColor: 'primary.main',
                      color: 'primary.main',
                      '&:hover': {
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        borderColor: 'primary.light',
                        transform: 'translateY(-2px)',
                      },
                    }}
                  >
                    Browse All Characters
                  </Button>
                )}
              </Stack>
            </Paper>
          </Box>
        </Fade>
      </Container>
    );
  }

  // Sort characters: user's characters first, then by star count, then by name
  const sortedCharacters = [...currentCharacters].sort((a, b) => {
    if (a.isOwner !== b.isOwner) {
      return a.isOwner ? -1 : 1;
    }
    if (a.starred !== b.starred) {
      return b.starred - a.starred;
    }
    return a.displayName.localeCompare(b.displayName);
  });

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Fade in timeout={800}>
        <Box>
          {/* Header */}
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 4 }}>
            <Box>
              <Typography variant="h3" sx={{ fontWeight: 800, mb: 1 }}>
                Characters
              </Typography>
              <Typography variant="h6" sx={{ color: 'text.secondary' }}>
                {currentCharacters.length} character{currentCharacters.length !== 1 ? 's' : ''} available
              </Typography>
            </Box>
            <Button
              variant="contained"
              startIcon={<PersonAddIcon />}
              onClick={handleCreateCharacterClick}
              sx={{
                px: 3,
                py: 1.5,
                fontWeight: 600,
                borderRadius: 2,
                background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
                  transform: 'translateY(-2px)',
                },
              }}
            >
              Create Character
            </Button>
          </Box>

          {/* Create Character Form */}
          <CreateCharacterForm
            isOpen={showCreateForm}
            onClose={handleFormClose}
            onSuccess={handleFormSuccess}
          />

          {/* Tab Navigation */}
          <Box sx={{ mb: 4 }}>
            <Tabs 
              value={activeTab} 
              onChange={handleTabChange}
              sx={{
                '& .MuiTabs-indicator': {
                  background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                },
                '& .MuiTab-root': {
                  color: 'text.secondary',
                  fontWeight: 600,
                  fontSize: '1rem',
                  textTransform: 'none',
                  '&.Mui-selected': {
                    color: 'primary.main',
                  },
                },
              }}
            >
              <Tab label="My Characters" />
              <Tab label="All Characters" />
            </Tabs>
          </Box>

          {/* Characters Grid */}
          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 3, alignItems: 'start' }}>
            {sortedCharacters.map((character) => (
              <CharacterCard 
                key={character.id}
                character={character} 
                onStarToggle={handleStarToggle}
                onDelete={handleDelete}
                onUpdate={handleUpdate}
                activeTab={activeTab}
                isEditing={editingCharacterId === character.id}
                onEditStart={handleEditStart}
                onEditClose={handleEditClose}
              />
            ))}
          </Box>
        </Box>
      </Fade>
    </Container>
  );
}; 