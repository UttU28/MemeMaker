from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from email_validator import validate_email, EmailNotValidError


class CharacterConfig(BaseModel):
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    nfeSteps: int = Field(default=34, ge=20, le=50)
    crossFadeDuration: float = Field(default=0.15, ge=0.0, le=1.0)
    removeSilences: bool = Field(default=True)


class CharacterUpdate(BaseModel):
    displayName: Optional[str] = Field(None, min_length=1, max_length=50)
    config: Optional[CharacterConfig] = None


class CharacterResponse(BaseModel):
    id: str
    displayName: str
    audioFile: Optional[str] = None
    config: CharacterConfig
    images: Dict[str, str] = Field(default_factory=dict)
    outputPrefix: str
    createdAt: str
    updatedAt: str
    hasAudio: bool = False
    imageCount: int = 0
    createdBy: Optional[str] = None  # User ID who created this character
    createdByName: Optional[str] = None  # Display name of the creator
    isOwner: bool = False  # Whether the current requesting user owns this character
    starred: int = 0  # Number of users who have starred this character
    isStarred: bool = False  # Whether the current user has starred this character


class SystemStatus(BaseModel):
    status: str
    totalCharacters: int
    timestamp: str
    apiDataDir: str


class ScriptRequest(BaseModel):
    selectedCharacters: List[str] = Field(..., min_items=2, max_items=5)
    prompt: str = Field(..., min_length=10, max_length=500)
    word: Optional[str] = Field(None, max_length=50)


class DialogueLine(BaseModel):
    speaker: str
    text: str
    audioFile: Optional[str] = None


class ScriptResponse(BaseModel):
    id: str
    selectedCharacters: List[str]
    originalPrompt: str
    word: Optional[str]
    dialogue: List[DialogueLine]
    createdAt: str
    updatedAt: str
    hasAudio: bool = False
    audioCount: int = 0
    finalVideoPath: Optional[str] = None
    videoDuration: Optional[float] = None
    videoSize: Optional[int] = None


class ScriptUpdate(BaseModel):
    dialogue: List[DialogueLine]


class AudioGenerationStatus(BaseModel):
    scriptId: str
    status: str
    totalLines: int
    processedLines: int
    completedLines: int
    failedLines: int
    startedAt: Optional[str] = None
    completedAt: Optional[str] = None
    errorMessage: Optional[str] = None


class AudioGenerationResponse(BaseModel):
    scriptId: str
    status: str
    message: str
    completedLines: int
    totalLines: int


class VideoGenerationStatus(BaseModel):
    scriptId: str
    status: str
    stage: str
    progress: float
    message: str
    startedAt: Optional[str] = None
    completedAt: Optional[str] = None
    errorMessage: Optional[str] = None
    finalVideoPath: Optional[str] = None


class VideoGenerationResponse(BaseModel):
    scriptId: str
    status: str
    message: str
    finalVideoPath: Optional[str] = None
    duration: Optional[float] = None
    videoSize: Optional[int] = None 


# Authentication Models

class SignupRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="User's full name")
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$', description="User's email address")
    password: str = Field(..., min_length=6, max_length=128, description="User's password")


class LoginRequest(BaseModel):
    email: str = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, max_length=128, description="User's password")


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    isVerified: bool = False
    subscription: str = "free"
    createdAt: str
    updatedAt: str


class AuthResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    user: Optional[UserResponse] = None
    expiresIn: Optional[int] = None  # Token expiration in seconds


# Star/Favorite Models

class StarResponse(BaseModel):
    success: bool
    message: str
    characterId: str
    starred: int  # Updated star count
    isStarred: bool  # User's current star status


class FavoriteCharacter(BaseModel):
    charId: str
    charName: str


# User Activity Models

class UserActivity(BaseModel):
    id: str
    type: str
    message: str
    timestamp: str
    scriptId: Optional[str] = None
    characterId: Optional[str] = None
    videoPath: Optional[str] = None


class UserActivityResponse(BaseModel):
    activities: List[UserActivity]
    totalCount: int
    limit: int


class ActivityStats(BaseModel):
    scriptActivities: int = 0
    characterActivities: int = 0
    videoActivities: int = 0
    totalActivities: int = 0
    lastActivityAt: Optional[str] = None