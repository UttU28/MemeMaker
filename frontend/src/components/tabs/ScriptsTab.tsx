import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
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
  VideoFile as VideoIcon,

  Chat as ChatIcon,
  ExpandMore as ExpandMoreIcon,
  Close as CloseIcon,
  Check as CheckIcon,
  Cancel as CancelIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  AddComment as AddCommentIcon,
} from '@mui/icons-material';
import { scriptAPI, characterAPI, type Script, type Character, type ScriptRequest, type DialogueLine, type ScriptUpdate, type VideoGenerationJobResponse } from '../../services/api';
import ConfirmDialog from '../ConfirmDialog';

interface ScriptCardProps {
  script: Script;
  onDelete: (scriptId: string) => Promise<void>;
  onUpdate: (scriptId: string, updatedScript: Script) => void;
  characters: Character[];
  autoEdit?: boolean;
}

const ScriptCard: React.FC<ScriptCardProps> = ({ script, onDelete, onUpdate, characters, autoEdit = false }) => {
  const navigate = useNavigate();
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDialogue, setShowDialogue] = useState(autoEdit);
  const [showFullPrompt, setShowFullPrompt] = useState(false);
  const [isEditing, setIsEditing] = useState(autoEdit);
  const [editingDialogue, setEditingDialogue] = useState<DialogueLine[]>(autoEdit ? [...script.dialogue] : []);
  const [isSaving, setIsSaving] = useState(false);
  const [showGenerateVideoDialog, setShowGenerateVideoDialog] = useState(false);
  const [isGeneratingVideo, setIsGeneratingVideo] = useState(false);
  const [isChangingScript, setIsChangingScript] = useState(autoEdit && script.finalVideoPath ? true : false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [hasEverMadeChanges, setHasEverMadeChanges] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to card when auto-editing
  useEffect(() => {
    if (autoEdit && cardRef.current) {
      setTimeout(() => {
        cardRef.current?.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'center' 
        });
      }, 100); // Small delay to ensure DOM is ready
    }
  }, [autoEdit]);

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

  const handleEditClick = () => {
    setEditingDialogue([...script.dialogue]);
    setIsEditing(true);
  };

  const handleEditCancel = () => {
    setIsEditing(false);
    setEditingDialogue([]);
    setHasUnsavedChanges(false);
    if (isChangingScript) {
      setHasEverMadeChanges(false); // Reset when canceling changes in change script mode
    }
  };

  const handleEditSave = async () => {
    setIsSaving(true);
    try {
      const updateData: ScriptUpdate = {
        dialogue: editingDialogue
      };
      const updatedScript = await scriptAPI.updateScript(script.id, updateData);
      
      if (isChangingScript) {
        // Keep the editing state open but mark as saved
        setHasUnsavedChanges(false);
        // Keep hasEverMadeChanges as true since we saved changes
      } else {
        // Normal edit flow - close editing
        setIsEditing(false);
        setEditingDialogue([]);
        setHasUnsavedChanges(false);
      }
      
      // Update the script locally without closing the dialogue
      onUpdate(script.id, updatedScript);
    } catch (error) {
      console.error('Error updating script:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleChangeScriptClick = () => {
    setIsChangingScript(true);
    setShowDialogue(true);
    setEditingDialogue([...script.dialogue]);
    setIsEditing(true);
    setHasUnsavedChanges(false);
    setHasEverMadeChanges(false); // Reset when starting change script mode
  };

  const handleChangeScriptCancel = () => {
    setIsChangingScript(false);
    setShowDialogue(false);
    setIsEditing(false);
    setEditingDialogue([]);
    setHasUnsavedChanges(false);
    setHasEverMadeChanges(false); // Reset when canceling
  };

  const handleGenerateVideoClick = () => {
    setShowGenerateVideoDialog(true);
  };

  const handleGenerateVideoConfirm = async () => {
    setIsGeneratingVideo(true);
    try {
      console.log('Generate Video confirmed for script ID:', script.id);
      
      // Call the video generation API
      const result: VideoGenerationJobResponse = await scriptAPI.generateVideo(script.id);
      
      if (result.job && (result.job.status === 'queued' || result.job.status === 'in_progress')) {
        // Close the dialog first
        setShowGenerateVideoDialog(false);
        
        // Navigate to videos page automatically
        navigate('/videos');
        
        console.log('Video generation started successfully:', result.message);
      } else {
        console.error('Video generation failed to start:', result.message);
        // Show error to user (you can add a toast/alert here)
      }
    } catch (error) {
      console.error('Error generating video:', error);
      // Show error to user (you can add a toast/alert here)
    } finally {
      setIsGeneratingVideo(false);
    }
  };

  const handleGenerateVideoCancel = () => {
    setShowGenerateVideoDialog(false);
  };

  const handleDialogueChange = (index: number, field: keyof DialogueLine, value: string) => {
    const newDialogue = [...editingDialogue];
    newDialogue[index] = { ...newDialogue[index], [field]: value };
    setEditingDialogue(newDialogue);
    
    // Check if there are unsaved changes
    if (!isChangingScript) {
      setHasUnsavedChanges(true);
    } else {
      // In change script mode, track that changes have been made
      setHasUnsavedChanges(true);
      setHasEverMadeChanges(true);
    }
  };

  const handleAddDialogueLine = () => {
    const newLine: DialogueLine = {
      speaker: script.selectedCharacters[0] || '',
      text: '',
    };
    setEditingDialogue([...editingDialogue, newLine]);
    
    // Check if there are unsaved changes
    if (!isChangingScript) {
      setHasUnsavedChanges(true);
    } else {
      // In change script mode, track that changes have been made
      setHasUnsavedChanges(true);
      setHasEverMadeChanges(true);
    }
  };

  const handleRemoveDialogueLine = (index: number) => {
    const newDialogue = editingDialogue.filter((_, i) => i !== index);
    setEditingDialogue(newDialogue);
    
    // Check if there are unsaved changes
    if (!isChangingScript) {
      setHasUnsavedChanges(true);
    } else {
      // In change script mode, track that changes have been made
      setHasUnsavedChanges(true);
      setHasEverMadeChanges(true);
    }
  };

  // Check if there are actual changes in the dialogue content
  const hasDialogueChanges = () => {
    if (!isChangingScript) return hasUnsavedChanges;
    
    // Compare lengths first
    if (editingDialogue.length !== script.dialogue.length) {
      return true;
    }
    
    // Compare each dialogue line
    for (let i = 0; i < editingDialogue.length; i++) {
      const original = script.dialogue[i];
      const edited = editingDialogue[i];
      
      if (original.speaker !== edited.speaker || original.text !== edited.text) {
        return true;
      }
    }
    
    return false;
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
        ref={cardRef}
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
          {/* Top Bar - Script Name + All Chips + Timestamp + Delete Button */}
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
                  icon={<ChatIcon sx={{ fontSize: '12px !important' }} />}
                  label={script.dialogue.length}
                  sx={{
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    color: '#8b5cf6',
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
                
                {/* Timestamp Chip */}
                <Chip
                  size="small"
                  label={`Created: ${formatDate(script.createdAt)}`}
                  sx={{
                    backgroundColor: 'rgba(148, 163, 184, 0.1)',
                    color: 'text.secondary',
                    fontWeight: 600,
                    fontSize: '0.75rem',
                  }}
                />
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
              <Box sx={{ mb: 3 }}>
                <Typography variant="body2" sx={{ color: 'text.secondary', fontWeight: 600 }}>
                Dialogue:
              </Typography>
              </Box>
              
              {isEditing ? (
                /* Edit Mode */
                <Box>
                  <Stack spacing={2.5}>
                    {editingDialogue.map((line, index) => (
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
                          <FormControl sx={{ mb: 1.5, maxWidth: 150 }}>
                            <Select
                              size="small"
                              value={line.speaker}
                              onChange={(e) => handleDialogueChange(index, 'speaker', e.target.value)}
                              variant="standard"
                              disableUnderline
                              sx={{
                                fontSize: '0.9rem',
                                fontWeight: 600,
                                color: 'primary.main',
                                minWidth: 80,
                                '& .MuiSelect-select': {
                                  paddingTop: 0,
                                  paddingBottom: 0,
                                  paddingLeft: 0,
                                  paddingRight: '20px !important',
                                },
                                '& .MuiSelect-icon': {
                                  fontSize: '16px',
                                  color: 'primary.main',
                                },
                                '&:hover': {
                                  '& .MuiSelect-select': {
                                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                                    borderRadius: 1,
                                    paddingLeft: 0.5,
                                    paddingRight: '24px !important',
                                  },
                                },
                              }}
                            >
                              {script.selectedCharacters.map((charId) => (
                                <MenuItem key={charId} value={charId}>
                                  {getCharacterName(charId)}
                                </MenuItem>
                              ))}
                            </Select>
                          </FormControl>
                          <TextField
                            fullWidth
                            multiline
                            minRows={1}
                            maxRows={6}
                            value={line.text}
                            onChange={(e) => handleDialogueChange(index, 'text', e.target.value)}
                            placeholder="Enter dialogue text..."
                            variant="standard"
                            sx={{
                              '& .MuiInput-root': {
                                fontSize: '0.85rem',
                                color: 'text.primary',
                                lineHeight: 1.5,
                                '&:before': {
                                  display: 'none',
                                },
                                '&:after': {
                                  display: 'none',
                                },
                                '&:hover:not(.Mui-disabled):before': {
                                  display: 'none',
                                },
                              },
                              '& .MuiInput-input': {
                                padding: 0,
                                '&::placeholder': {
                                  color: 'rgba(148, 163, 184, 0.7)',
                                  opacity: 1,
                                },
                              },
                            }}
                          />
                        </Box>
                        <IconButton
                          size="small"
                          onClick={() => handleRemoveDialogueLine(index)}
                          disabled={editingDialogue.length <= 1}
                          sx={{
                            color: 'error.main',
                            opacity: 0.7,
                            '&:hover': {
                              backgroundColor: 'rgba(239, 68, 68, 0.1)',
                              opacity: 1,
                            },
                          }}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Box>
                    ))}
                  </Stack>
                  
                  {/* Add new dialogue line button */}
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<AddCommentIcon />}
                    onClick={handleAddDialogueLine}
                    sx={{
                      mt: 2,
                      fontSize: '0.75rem',
                      py: 0.5,
                      px: 1.5,
                      borderRadius: 1.5,
                      fontWeight: 600,
                      borderColor: 'rgba(34, 197, 94, 0.3)',
                      color: '#22c55e',
                      '&:hover': {
                        backgroundColor: 'rgba(34, 197, 94, 0.1)',
                        borderColor: '#22c55e',
                      },
                    }}
                  >
                    Add Line
                  </Button>
                </Box>
              ) : (
                /* View Mode */
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
              )}
            </Box>
          </Collapse>

          {/* Bottom Bar - Action Buttons */}
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            pt: 2,
            borderTop: '1px solid rgba(148, 163, 184, 0.1)',
          }}>
            {/* Action Buttons - Left Aligned */}
            <Stack direction="row" spacing={1.5}>
              {/* Video Generation Status - Subtle Progress */}
              {script.videoJobStatus === 'queued' || script.videoJobStatus === 'in_progress' ? (
                /* Video Generation In Progress - Subtle Display */
                <Box sx={{ flex: 1, maxWidth: 400 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Typography variant="body2" sx={{ fontSize: '0.8rem', fontWeight: 600, color: '#f59e0b', flex: 1 }}>
                      Video Generation in Progress...
                    </Typography>
                    <Typography variant="caption" sx={{ fontSize: '0.7rem', color: 'text.secondary', fontWeight: 500 }}>
                      {Math.round(script.videoJobProgress || 0)}%
                    </Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={script.videoJobProgress || 0} 
                    sx={{
                      height: 3,
                      borderRadius: 1.5,
                      backgroundColor: 'rgba(245, 158, 11, 0.15)',
                      '& .MuiLinearProgress-bar': {
                        background: 'linear-gradient(90deg, #f59e0b 0%, #d97706 100%)',
                        borderRadius: 1.5,
                      }
                    }}
                  />
                </Box>
              ) : script.videoJobStatus === 'completed' && script.finalVideoPath ? (
                /* Video Completed */
                !isChangingScript ? (
                  <Stack direction="row" spacing={1.5}>
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={<PlayIcon />}
                      onClick={() => navigate(`/videos?script=${script.id}`)}
                      sx={{
                        fontSize: '0.8rem',
                        py: 1,
                        px: 2.5,
                        borderRadius: 2,
                        fontWeight: 600,
                        background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
                        '&:hover': {
                          background: 'linear-gradient(135deg, #16a34a 0%, #15803d 100%)',
                          transform: 'translateY(-1px)',
                          boxShadow: '0 4px 12px rgba(34, 197, 94, 0.3)',
                        },
                      }}
                    >
                      View Video
                    </Button>
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<EditIcon />}
                      onClick={handleChangeScriptClick}
                      sx={{
                        fontSize: '0.8rem',
                        py: 1,
                        px: 2.5,
                        borderRadius: 2,
                        fontWeight: 600,
                        borderColor: 'rgba(99, 102, 241, 0.3)',
                        color: 'primary.main',
                        '&:hover': {
                          backgroundColor: 'rgba(99, 102, 241, 0.1)',
                          borderColor: 'primary.main',
                          transform: 'translateY(-1px)',
                          boxShadow: '0 4px 12px rgba(99, 102, 241, 0.2)',
                        },
                      }}
                    >
                      Change Script
                    </Button>
                  </Stack>
                ) : (
                  /* Change Script Mode - Generate Video Button */
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<VideoIcon />}
                    onClick={handleGenerateVideoClick}
                    disabled={!hasEverMadeChanges || hasUnsavedChanges || isSaving}
                    sx={{
                      fontSize: '0.8rem',
                      py: 1,
                      px: 2.5,
                      borderRadius: 2,
                      fontWeight: 600,
                      borderColor: (!hasEverMadeChanges || hasUnsavedChanges || isSaving) ? 'rgba(148, 163, 184, 0.3)' : 'rgba(245, 158, 11, 0.5)',
                      color: (!hasEverMadeChanges || hasUnsavedChanges || isSaving) ? 'text.disabled' : '#f59e0b',
                      '&:hover': {
                        backgroundColor: (!hasEverMadeChanges || hasUnsavedChanges || isSaving) ? 'transparent' : 'rgba(245, 158, 11, 0.1)',
                        borderColor: (!hasEverMadeChanges || hasUnsavedChanges || isSaving) ? 'rgba(148, 163, 184, 0.3)' : '#f59e0b',
                        transform: (!hasEverMadeChanges || hasUnsavedChanges || isSaving) ? 'none' : 'translateY(-1px)',
                        boxShadow: (!hasEverMadeChanges || hasUnsavedChanges || isSaving) ? 'none' : '0 4px 12px rgba(245, 158, 11, 0.2)',
                      },
                      '&:disabled': {
                        borderColor: 'rgba(148, 163, 184, 0.3)',
                        color: 'text.disabled',
                      },
                    }}
                  >
                    Generate Video
                  </Button>
                )
              ) : script.videoJobStatus === 'failed' ? (
                /* Video Generation Failed */
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<VideoIcon />}
                  onClick={showDialogue ? handleGenerateVideoClick : () => setShowDialogue(true)}
                  sx={{
                    fontSize: '0.8rem',
                    py: 1,
                    px: 2.5,
                    borderRadius: 2,
                    fontWeight: 600,
                    borderColor: 'rgba(239, 68, 68, 0.5)',
                    color: '#ef4444',
                    '&:hover': {
                      backgroundColor: 'rgba(239, 68, 68, 0.1)',
                      borderColor: '#ef4444',
                      transform: 'translateY(-1px)',
                      boxShadow: '0 4px 12px rgba(239, 68, 68, 0.2)',
                    },
                  }}
                >
                  {showDialogue ? 'Retry Video' : 'View Dialogue'}
                </Button>
              ) : (
                /* Ready for Video Generation - Always show Generate Video button */
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={showDialogue ? <VideoIcon /> : <ExpandMoreIcon />}
                  onClick={showDialogue ? handleGenerateVideoClick : () => setShowDialogue(true)}
                  sx={{
                    fontSize: '0.8rem',
                    py: 1,
                    px: 2.5,
                    borderRadius: 2,
                    fontWeight: 600,
                    borderColor: showDialogue ? 'rgba(245, 158, 11, 0.5)' : 'primary.main',
                    color: showDialogue ? '#f59e0b' : 'primary.main',
                    '&:hover': {
                      backgroundColor: showDialogue ? 'rgba(245, 158, 11, 0.1)' : 'rgba(99, 102, 241, 0.1)',
                      borderColor: showDialogue ? '#f59e0b' : 'primary.main',
                      transform: 'translateY(-1px)',
                      boxShadow: showDialogue ? '0 4px 12px rgba(245, 158, 11, 0.2)' : '0 4px 12px rgba(99, 102, 241, 0.2)',
                    },
                  }}
                >
                  {showDialogue ? 'Generate Video' : 'View Dialogue'}
                </Button>
              )}
              
              {/* Edit Script Button - Only show when dialogue is expanded and not editing */}
              {showDialogue && !isEditing && (
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<EditIcon />}
                  onClick={handleEditClick}
                  sx={{
                    fontSize: '0.8rem',
                    py: 1,
                    px: 2.5,
                    borderRadius: 2,
                    fontWeight: 600,
                    borderColor: 'rgba(99, 102, 241, 0.3)',
                    color: 'primary.main',
                    '&:hover': {
                      backgroundColor: 'rgba(99, 102, 241, 0.1)',
                      borderColor: 'primary.main',
                      transform: 'translateY(-1px)',
                      boxShadow: '0 4px 12px rgba(99, 102, 241, 0.2)',
                    },
                  }}
                >
                  Edit Script
                </Button>
              )}
            </Stack>

            {/* Dialogue Cancel Button - Right Aligned */}
            {showDialogue && !isEditing && (
              <Button
                variant="outlined"
                size="small"
                startIcon={<CloseIcon />}
                onClick={() => setShowDialogue(false)}
                sx={{
                  fontSize: '0.8rem',
                  py: 1,
                  px: 2.5,
                  borderRadius: 2,
                  fontWeight: 600,
                  borderColor: 'rgba(148, 163, 184, 0.3)',
                  color: 'text.secondary',
                  '&:hover': {
                    backgroundColor: 'rgba(148, 163, 184, 0.1)',
                    borderColor: 'rgba(148, 163, 184, 0.5)',
                    transform: 'translateY(-1px)',
                  },
                }}
              >
                Cancel
              </Button>
            )}

            {/* Edit Mode Buttons - Right Aligned */}
            {isEditing && (
              <Stack direction="row" spacing={1.5}>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={isChangingScript ? handleChangeScriptCancel : handleEditCancel}
                  disabled={isSaving}
                  sx={{
                    fontSize: '0.8rem',
                    py: 1,
                    px: 2.5,
                    borderRadius: 2,
                    fontWeight: 600,
                    borderColor: 'rgba(148, 163, 184, 0.3)',
                    color: 'text.secondary', 
                    '&:hover': {
                      backgroundColor: 'rgba(148, 163, 184, 0.1)',
                      borderColor: 'rgba(148, 163, 184, 0.5)',
                      transform: 'translateY(-1px)',
                    },
                  }}
                >
                  Cancel
                </Button>
                <Button
                  variant="contained"
                  size="small"
                  startIcon={<SaveIcon />}
                  onClick={handleEditSave}
                  disabled={isSaving || !hasDialogueChanges()}
                  sx={{
                    fontSize: '0.8rem',
                    py: 1,
                    px: 2.5,
                    borderRadius: 2,
                    fontWeight: 600,
                    background: (isSaving || !hasDialogueChanges()) 
                      ? 'rgba(148, 163, 184, 0.3)' 
                      : 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
                    color: (isSaving || !hasDialogueChanges()) ? 'text.disabled' : 'white',
                    '&:hover': {
                      background: (isSaving || !hasDialogueChanges()) 
                        ? 'rgba(148, 163, 184, 0.3)' 
                        : 'linear-gradient(135deg, #16a34a 0%, #15803d 100%)',
                      transform: (isSaving || !hasDialogueChanges()) ? 'none' : 'translateY(-1px)',
                      boxShadow: (isSaving || !hasDialogueChanges()) ? 'none' : '0 4px 12px rgba(34, 197, 94, 0.3)',
                    },
                    '&:disabled': {
                      background: 'rgba(148, 163, 184, 0.3)',
                      color: 'text.disabled',
                    },
                  }}
                >
                  {isSaving ? 'Saving...' : 'Save'}
                </Button>
              </Stack>
            )}
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

          {/* Generate Video Confirmation Dialog */}
          <ConfirmDialog
            open={showGenerateVideoDialog}
            onClose={handleGenerateVideoCancel}
            onConfirm={handleGenerateVideoConfirm}
            title="Generate Video"
            message={`Are you sure you want to generate the video? This will automatically generate audio for all dialogue lines and then create the video. The process may take a few minutes.`}
            confirmText="Generate Video"
            cancelText="Cancel"
            variant="warning"
            loading={isGeneratingVideo}
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
  const [searchParams, setSearchParams] = useSearchParams();
  const targetScriptId = searchParams.get('edit');

  const fetchScripts = async (showLoader: boolean = true) => {
    try {
      if (showLoader) {
        setLoading(true);
      }
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
      if (showLoader) {
        setLoading(false);
      }
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

  const handleUpdateScript = (scriptId: string, updatedScript: Script) => {
    setScripts(prev => 
      prev.map(script => 
        script.id === scriptId ? updatedScript : script
      )
    );
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

  const intervalRef = useRef<number | null>(null);

  useEffect(() => {
    fetchScripts();
  }, []);

  // Clear URL parameter after auto-editing is handled
  useEffect(() => {
    if (targetScriptId && scripts.length > 0) {
      // Clear the edit parameter from URL after a delay to allow auto-expansion
      setTimeout(() => {
        setSearchParams({});
      }, 1000);
    }
  }, [targetScriptId, scripts.length, setSearchParams]);

  // Auto-refresh when there are active video jobs
  useEffect(() => {
    const activeVideoJobs = scripts.filter(script => 
      script.videoJobStatus === 'queued' || script.videoJobStatus === 'in_progress'
    );

    // Clear existing interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    if (activeVideoJobs.length > 0) {
      console.log(`🔄 Starting polling for ${activeVideoJobs.length} active video jobs:`, 
        activeVideoJobs.map(s => `${s.id.slice(-6)}: ${s.videoJobStatus}`));
      
      intervalRef.current = setInterval(() => {
        fetchScripts(false); // Silent refresh without loader
      }, 5000); // Poll every 3 seconds
    } else {
      console.log('✅ No active video jobs - stopping polling');
    }

    // Cleanup function
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [scripts.map(s => s.videoJobStatus || 'none').join(',')]); // Only depend on video job statuses, handle undefined

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
        
        <Box>
          {Array.from({ length: 3 }).map((_, idx) => (
            <Card
              key={idx}
              elevation={0}
              sx={{
                borderRadius: 3,
                background: 'rgba(30, 41, 59, 0.6)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(148, 163, 184, 0.1)',
                mb: 2,
              }}
            >
              <CardContent sx={{ p: 3 }}>
                {/* Top Bar - Script Name + Chips + Delete Button */}
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Skeleton variant="circular" width={20} height={20} />
                      <Skeleton variant="text" width={120} height={24} />
                    </Box>
                    
                    {/* Chips/Bubbles */}
                    <Stack direction="row" spacing={1}>
                      <Skeleton variant="rounded" width={40} height={24} sx={{ borderRadius: 2 }} />
                      <Skeleton variant="rounded" width={40} height={24} sx={{ borderRadius: 2 }} />
                      <Skeleton variant="rounded" width={50} height={24} sx={{ borderRadius: 2 }} />
                      <Skeleton variant="rounded" width={80} height={24} sx={{ borderRadius: 2 }} />
                      <Skeleton variant="rounded" width={100} height={24} sx={{ borderRadius: 2 }} />
                    </Stack>
                  </Box>
                  
                  {/* Delete Button */}
                  <Skeleton variant="circular" width={32} height={32} />
                </Box>

                {/* Prompt Section */}
                <Box sx={{ mb: 3 }}>
                  <Skeleton variant="text" width={60} height={20} sx={{ mb: 1 }} />
                  <Box sx={{ 
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    p: 1.5,
                    borderRadius: 2,
                    border: '1px solid rgba(99, 102, 241, 0.2)',
                  }}>
                    <Skeleton variant="text" width="100%" height={20} />
                    <Skeleton variant="text" width="80%" height={20} />
                  </Box>
                </Box>

                {/* Buttons Section */}
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Stack direction="row" spacing={1.5}>
                    <Skeleton variant="rounded" width={120} height={36} sx={{ borderRadius: 2 }} />
                  </Stack>
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
            <Button color="inherit" size="small" onClick={() => fetchScripts()}>
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
            {scripts
              .sort((a, b) => {
                // Sort by updatedAt first (most recent first)
                const aUpdated = new Date(a.updatedAt).getTime();
                const bUpdated = new Date(b.updatedAt).getTime();
                
                if (aUpdated !== bUpdated) {
                  return bUpdated - aUpdated; // Most recent updated first
                }
                
                // If updatedAt is the same, sort by createdAt (most recent first)
                const aCreated = new Date(a.createdAt).getTime();
                const bCreated = new Date(b.createdAt).getTime();
                return bCreated - aCreated; // Most recent created first
              })
              .map((script) => (
                <ScriptCard 
                  key={script.id}
                  script={script} 
                  onDelete={handleDelete}
                  onUpdate={handleUpdateScript}
                  characters={characters}
                  autoEdit={script.id === targetScriptId}
                />
              ))}
          </Box>
        </Box>
      </Fade>
    </Container>
  );
}; 