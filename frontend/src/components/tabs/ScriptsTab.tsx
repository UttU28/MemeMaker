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
  Chip,
  IconButton,
  Skeleton,
  Alert,
  Tooltip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  OutlinedInput,
  Collapse,
  LinearProgress,
  Avatar,
} from '@mui/material';
import {
  Description as ScriptIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  PlayArrow as PlayIcon,
  PeopleAlt as PeopleIcon,
  Mic as MicIcon,
  VideoFile as VideoIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Close as CloseIcon,
  Check as CheckIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import { scriptAPI, characterAPI, type Script, type Character, type ScriptRequest } from '../../services/api';
import ConfirmDialog from '../ConfirmDialog';

interface ScriptCardProps {
  script: Script;
  onDelete: (scriptId: string) => Promise<void>;
  characters: Character[];
}

const ScriptCard: React.FC<ScriptCardProps> = ({ script, onDelete, characters }) => {
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDialogue, setShowDialogue] = useState(false);
  const [showFullPrompt, setShowFullPrompt] = useState(false);

  const handleDeleteClick = () => {
    setShowDeleteDialog(true);
  };

  const handleDeleteConfirm = async () => {
    setIsDeleting(true);
    try {
      await onDelete(script.id);
      setShowDeleteDialog(false);
    } catch (error) {
      console.error('Error deleting script:', error);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteDialog(false);
  };

  const getCharacterName = (characterId: string) => {
    const character = characters.find(c => c.id === characterId);
    return character ? character.displayName : characterId;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <Fade in timeout={800}>
      <Card
        elevation={0}
        sx={{
          borderRadius: 3,
          background: 'rgba(30, 41, 59, 0.6)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(148, 163, 184, 0.1)',
          '&:hover': {
            border: '1px solid rgba(99, 102, 241, 0.3)',
          },
          mb: 2,
        }}
      >
        <CardContent sx={{ p: 3 }}>
          {/* Top Bar - Script Name + All Chips + Delete Button */}
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <ScriptIcon sx={{ color: 'primary.main', fontSize: 20 }} />
                <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '1rem' }}>
                  Script #{script.id.slice(-6)}
                </Typography>
              </Box>
              
              {/* All Chips/Bubbles */}
              <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap' }}>
                <Chip
                  size="small"
                  icon={<PeopleIcon sx={{ fontSize: '12px !important' }} />}
                  label={script.selectedCharacters.length}
                  sx={{
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    color: 'primary.main',
                    fontWeight: 600,
                    fontSize: '0.75rem',
                  }}
                />
                <Chip
                  size="small"
                  icon={<MicIcon sx={{ fontSize: '12px !important' }} />}
                  label={script.audioCount}
                  sx={{
                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                    color: '#22c55e',
                    fontWeight: 600,
                    fontSize: '0.75rem',
                  }}
                />
                {script.hasAudio && (
                  <Chip
                    size="small"
                    icon={<VideoIcon sx={{ fontSize: '12px !important' }} />}
                    label="Ready"
                    sx={{
                      backgroundColor: 'rgba(245, 158, 11, 0.1)',
                      color: '#f59e0b',
                      fontWeight: 600,
                      fontSize: '0.75rem',
                    }}
                  />
                )}
                
                {/* Character Chips */}
                {script.selectedCharacters.map((charId) => (
                  <Chip
                    key={charId}
                    size="small"
                    label={getCharacterName(charId)}
                    sx={{
                      backgroundColor: 'rgba(34, 197, 94, 0.1)',
                      color: '#22c55e',
                      fontWeight: 600,
                      fontSize: '0.75rem',
                    }}
                  />
                ))}
              </Stack>
            </Box>
            
            {/* Delete Button - Top Right */}
            <Tooltip title="Delete script">
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
          </Box>

          {/* Prompt Section */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="body2" sx={{ color: 'text.secondary', mb: 1, fontWeight: 600 }}>
              Prompt:
            </Typography>
            <Box sx={{ 
              backgroundColor: 'rgba(99, 102, 241, 0.1)',
              p: 1.5,
              borderRadius: 2,
              border: '1px solid rgba(99, 102, 241, 0.2)',
            }}>
              <Typography 
                variant="body2" 
                sx={{ 
                  color: 'text.primary',
                  fontStyle: 'italic',
                  lineHeight: 1.4,
                  display: showFullPrompt ? 'block' : '-webkit-box',
                  WebkitLineClamp: showFullPrompt ? 'none' : 2,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden',
                  wordBreak: 'break-word',
                }}
              >
                "{script.originalPrompt}"
              </Typography>
              {script.originalPrompt.length > 100 && (
                <Button
                  size="small"
                  onClick={() => setShowFullPrompt(!showFullPrompt)}
                  sx={{
                    mt: 1,
                    fontSize: '0.7rem',
                    color: 'primary.main',
                    textTransform: 'none',
                    p: 0,
                    minWidth: 'auto',
                    '&:hover': {
                      backgroundColor: 'transparent',
                      textDecoration: 'underline',
                    },
                  }}
                >
                  {showFullPrompt ? 'Show Less' : 'Show More'}
                </Button>
              )}
            </Box>
          </Box>

                    {/* Dialogue Section */}
          <Collapse 
            in={showDialogue}
            timeout={500}
            sx={{
              '& .MuiCollapse-wrapper': {
                '& .MuiCollapse-wrapperInner': {
                  paddingBottom: 2,
                }
              }
            }}
          >
            <Box sx={{ 
              mb: 0,
            }}>
              <Typography variant="body2" sx={{ color: 'text.secondary', mb: 3, fontWeight: 600 }}>
                Dialogue:
              </Typography>
              <Stack spacing={2.5}>
                {script.dialogue.map((line, index) => (
                  <Box
                    key={index}
                    sx={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: 1.5,
                      p: 1,
                      backgroundColor: 'rgba(148, 163, 184, 0.08)',
                      borderRadius: 2,
                      border: '1px solid rgba(148, 163, 184, 0.15)',
                      '&:hover': {
                        backgroundColor: 'rgba(148, 163, 184, 0.12)',
                        borderColor: 'rgba(99, 102, 241, 0.2)',
                        transform: 'translateY(-1px)',
                      },
                    }}
                  >
                    <Avatar
                      sx={{
                        width: 36,
                        height: 36,
                        backgroundColor: 'primary.main',
                        fontSize: '0.85rem',
                        flexShrink: 0,
                        '&:hover': {
                          transform: 'scale(1.05)',
                        },
                      }}
                    >
                      {getCharacterName(line.speaker).charAt(0)}
                    </Avatar>
                    <Box sx={{ flex: 1, minWidth: 0 }}>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          fontSize: '0.9rem', 
                          fontWeight: 600, 
                          color: 'primary.main',
                        }}
                      >
                        {getCharacterName(line.speaker)}
                      </Typography>
                                              <Typography 
                          variant="body2" 
                          sx={{ 
                            fontSize: '0.85rem', 
                            color: 'text.primary',
                            lineHeight: 1.5,
                            wordBreak: 'break-word'
                          }}
                        >
                          {line.text}
                        </Typography>
                    </Box>
                  </Box>
                ))}
              </Stack>
            </Box>
          </Collapse>

          {/* Bottom Bar - Action Buttons (Left) and Date (Right) */}
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            pt: 2,
            borderTop: '1px solid rgba(148, 163, 184, 0.1)',
          }}>
            {/* Action Buttons - Left Aligned */}
            <Stack direction="row" spacing={1.5}>
              <Button
                variant="contained"
                size="small"
                startIcon={<PlayIcon />}
                disabled={!script.hasAudio}
                sx={{
                  fontSize: '0.8rem',
                  py: 1,
                  px: 2.5,
                  borderRadius: 2,
                  fontWeight: 600,
                  background: script.hasAudio 
                    ? 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)'
                    : 'rgba(148, 163, 184, 0.3)',
                  '&:hover': {
                    background: script.hasAudio 
                      ? 'linear-gradient(135deg, #16a34a 0%, #15803d 100%)'
                      : 'rgba(148, 163, 184, 0.3)',
                    transform: script.hasAudio ? 'translateY(-1px)' : 'none',
                    boxShadow: script.hasAudio ? '0 4px 12px rgba(34, 197, 94, 0.3)' : 'none',
                  },
                }}
              >
                {script.hasAudio ? 'Video' : 'Processing...'}
              </Button>
              <Button
                variant="outlined"
                size="small"
                startIcon={showDialogue ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                onClick={() => setShowDialogue(!showDialogue)}
                sx={{
                  fontSize: '0.8rem',
                  py: 1,
                  px: 2.5,
                  borderRadius: 2,
                  fontWeight: 600,
                  borderColor: 'primary.main',
                  color: 'primary.main',
                  '&:hover': {
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    borderColor: 'primary.dark',
                    transform: 'translateY(-1px)',
                    boxShadow: '0 4px 12px rgba(99, 102, 241, 0.2)',
                  },
                }}
              >
                {showDialogue ? 'Hide Dialogue' : 'Show Dialogue'}
              </Button>
            </Stack>

            {/* Date - Right Aligned */}
            <Typography variant="body2" sx={{ 
              color: 'text.secondary', 
              fontSize: '0.75rem',
              fontStyle: 'italic',
              opacity: 0.8,
            }}>
              Created: {formatDate(script.createdAt)}
            </Typography>
          </Box>

          {/* Delete Confirmation Dialog */}
          <ConfirmDialog
            open={showDeleteDialog}
            onClose={handleDeleteCancel}
            onConfirm={handleDeleteConfirm}
            title="Delete Script"
            message={`Are you sure you want to delete this script? This action cannot be undone.`}
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

interface CreateScriptFormData {
  selectedCharacters: string[];
  prompt: string;
}

const CreateScriptForm: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (newScript: Script) => void;
  characters: Character[];
}> = ({ isOpen, onClose, onSuccess, characters }) => {
  const [formData, setFormData] = useState<CreateScriptFormData>({
    selectedCharacters: [],
    prompt: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (field: keyof CreateScriptFormData, value: string | string[]) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError(null);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (formData.selectedCharacters.length < 2) {
      setError('Please select at least 2 characters');
      return;
    }

    if (formData.prompt.trim().length < 10) {
      setError('Prompt must be at least 10 characters long');
      return;
    }

    if (formData.prompt.trim().length > 2000) {
      setError('Prompt must be less than 2000 characters');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const scriptRequest: ScriptRequest = {
        selectedCharacters: formData.selectedCharacters,
        prompt: formData.prompt.trim(),
      };

      const newScript = await scriptAPI.createScript(scriptRequest);
      onSuccess(newScript);
      handleCancel();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create script. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      selectedCharacters: [],
      prompt: '',
    });
    setError(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <Paper
      elevation={0}
      sx={{
        mb: 4,
        borderRadius: 3,
        background: 'rgba(30, 41, 59, 0.8)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(148, 163, 184, 0.1)',
        overflow: 'hidden',
      }}
    >
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            Create New Script
          </Typography>
          <IconButton onClick={handleCancel}>
            <CloseIcon />
          </IconButton>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <Stack spacing={3}>
            {/* Character Selection */}
            <FormControl fullWidth>
              <InputLabel>Select Characters (2-5)</InputLabel>
              <Select
                multiple
                value={formData.selectedCharacters}
                onChange={(e) => handleInputChange('selectedCharacters', e.target.value as string[])}
                input={<OutlinedInput label="Select Characters (2-5)" />}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value) => {
                      const character = characters.find(c => c.id === value);
                      return (
                        <Chip
                          key={value}
                          label={character ? character.displayName : value}
                          size="small"
                          sx={{ backgroundColor: 'rgba(99, 102, 241, 0.1)' }}
                        />
                      );
                    })}
                  </Box>
                )}
              >
                {characters.map((character) => (
                  <MenuItem key={character.id} value={character.id}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                      <Typography sx={{ flex: 1 }}>
                        {character.displayName}
                      </Typography>
                      {character.isOwner ? (
                        <Chip
                          size="small"
                          label="You"
                          sx={{
                            backgroundColor: 'rgba(99, 102, 241, 0.1)',
                            color: 'primary.main',
                            fontWeight: 600,
                            fontSize: '0.75rem',
                          }}
                        />
                      ) : (
                        <Chip
                          size="small"
                          label="⭐"
                          sx={{
                            backgroundColor: 'rgba(245, 158, 11, 0.1)',
                            color: '#f59e0b',
                            fontWeight: 600,
                            fontSize: '0.75rem',
                          }}
                        />
                      )}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* Prompt */}
            <TextField
              fullWidth
              label="Script Prompt"
              placeholder="Describe what you want the characters to talk about..."
              value={formData.prompt}
              onChange={(e) => handleInputChange('prompt', e.target.value)}
              multiline
              rows={6}
              inputProps={{ maxLength: 2000 }}
              helperText={`${formData.prompt.length}/2000 characters`}
            />



            {/* Action Buttons */}
            <Stack direction="row" spacing={2}>
              <Button
                type="submit"
                variant="contained"
                disabled={loading}
                startIcon={loading ? null : <CheckIcon />}
                sx={{
                  flex: 1,
                  py: 1.5,
                  fontWeight: 600,
                  background: loading 
                    ? 'linear-gradient(135deg, #6b7280 0%, #9ca3af 100%)'
                    : 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                  '&:hover': {
                    background: loading 
                      ? 'linear-gradient(135deg, #6b7280 0%, #9ca3af 100%)'
                      : 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
                  },
                }}
              >
                {loading ? '🤖 Generating Script with AI...' : 'Create Script'}
              </Button>
              <Button
                variant="outlined"
                onClick={handleCancel}
                disabled={loading}
                startIcon={<CancelIcon />}
                sx={{
                  borderColor: 'text.secondary',
                  color: 'text.secondary',
                  '&:hover': {
                    borderColor: 'text.primary',
                    color: 'text.primary',
                  },
                }}
              >
                Cancel
              </Button>
            </Stack>
          </Stack>
        </form>

        {loading && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" sx={{ color: 'text.secondary', mb: 1, textAlign: 'center' }}>
              🤖 AI is creating your script... This may take a few seconds
            </Typography>
            <LinearProgress 
              sx={{
                height: 6,
                borderRadius: 3,
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                '& .MuiLinearProgress-bar': {
                  background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                  borderRadius: 3,
                }
              }}
            />
          </Box>
        )}
      </Box>
    </Paper>
  );
};

export const ScriptsTab: React.FC = () => {
  const [scripts, setScripts] = useState<Script[]>([]);
  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);

  const fetchScripts = async () => {
    try {
      setLoading(true);
      const [scriptsData, myCharactersData, myFavoritesData] = await Promise.all([
        scriptAPI.getMyScripts(),
        characterAPI.getMyCharacters(),
        characterAPI.getMyFavorites(),
      ]);
      
      // Combine owned characters and favorites, avoiding duplicates
      const combinedCharacters = [...myCharactersData];
      myFavoritesData.forEach(favoriteChar => {
        // Only add if not already in the list (user hasn't favorited their own character)
        if (!combinedCharacters.some(char => char.id === favoriteChar.id)) {
          combinedCharacters.push(favoriteChar);
        }
      });
      
      setScripts(scriptsData);
      setCharacters(combinedCharacters);
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load scripts';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (scriptId: string) => {
    try {
      await scriptAPI.deleteScript(scriptId);
      setScripts(prev => prev.filter(script => script.id !== scriptId));
    } catch (err) {
      console.error('Error deleting script:', err);
      throw err;
    }
  };

  const handleCreateScriptClick = () => {
    setShowCreateForm(true);
  };

  const handleFormClose = () => {
    setShowCreateForm(false);
  };

  const handleFormSuccess = (newScript: Script) => {
    // Add the new script to the beginning of the scripts array
    setScripts(prev => [newScript, ...prev]);
    setShowCreateForm(false);
    
    // Show success feedback
    console.log('✅ Script created successfully:', newScript.id);
  };

  useEffect(() => {
    fetchScripts();
  }, []);

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ mb: 4 }}>
          <Typography variant="h3" sx={{ fontWeight: 800, mb: 2 }}>
            Scripts
          </Typography>
          <Typography variant="h6" sx={{ color: 'text.secondary', mb: 4 }}>
            Create and manage your AI-generated scripts
          </Typography>
        </Box>
        
        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: 3 }}>
          {Array.from({ length: 6 }).map((_, idx) => (
            <Card sx={{ height: 400 }} key={idx}>
              <CardContent sx={{ p: 3 }}>
                <Skeleton variant="text" height={32} sx={{ mb: 2 }} />
                <Skeleton variant="text" height={24} sx={{ mb: 2 }} />
                <Skeleton variant="rectangular" height={100} sx={{ borderRadius: 2, mb: 2 }} />
                <Stack spacing={1}>
                  <Skeleton variant="text" height={20} />
                  <Skeleton variant="text" height={20} />
                  <Skeleton variant="text" height={20} />
                </Stack>
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
            <Button color="inherit" size="small" onClick={fetchScripts}>
              Retry
            </Button>
          }
        >
          {error}
        </Alert>
      </Container>
    );
  }

  if (scripts.length === 0) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Fade in timeout={800}>
          <Box>
            {/* Header */}
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 4 }}>
              <Box>
                <Typography variant="h3" sx={{ fontWeight: 800, mb: 1 }}>
                  Scripts
                </Typography>
                <Typography variant="h6" sx={{ color: 'text.secondary' }}>
                  Create and manage your AI-generated scripts
                </Typography>
              </Box>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={handleCreateScriptClick}
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
                Create Script
              </Button>
            </Box>

            {/* Create Script Form */}
            <CreateScriptForm
              isOpen={showCreateForm}
              onClose={handleFormClose}
              onSuccess={handleFormSuccess}
              characters={characters}
            />

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
                <ScriptIcon sx={{ fontSize: 60, color: 'white' }} />
              </Box>
              
              <Typography variant="h4" sx={{ fontWeight: 700, mb: 2 }}>
                No Scripts Yet
              </Typography>
              
              <Typography variant="h6" sx={{ color: 'text.secondary', mb: 4, maxWidth: 500, mx: 'auto' }}>
                Create your first script to generate videos with AI characters. Select characters, provide a prompt, and let AI create engaging dialogues for you.
              </Typography>
              
              <Button
                variant="contained"
                size="large"
                startIcon={<AddIcon />}
                onClick={handleCreateScriptClick}
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
                Create Your First Script
              </Button>
            </Paper>
          </Box>
        </Fade>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Fade in timeout={800}>
        <Box>
          {/* Header */}
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 4 }}>
            <Box>
              <Typography variant="h3" sx={{ fontWeight: 800, mb: 1 }}>
                Scripts
              </Typography>
              <Typography variant="h6" sx={{ color: 'text.secondary' }}>
                {scripts.length} script{scripts.length !== 1 ? 's' : ''} created
              </Typography>
            </Box>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleCreateScriptClick}
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
              Create Script
            </Button>
          </Box>

          {/* Create Script Form */}
          <CreateScriptForm
            isOpen={showCreateForm}
            onClose={handleFormClose}
            onSuccess={handleFormSuccess}
            characters={characters}
          />

          {/* Scripts List */}
          <Box>
            {scripts.map((script) => (
              <ScriptCard 
                key={script.id}
                script={script} 
                onDelete={handleDelete}
                characters={characters}
              />
            ))}
          </Box>
        </Box>
      </Fade>
    </Container>
  );
}; 