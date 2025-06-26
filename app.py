#!/usr/bin/env python3

import json
import os
import shutil
import uuid
import time
import requests
import subprocess
import random
import glob
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import logging
from openai import OpenAI
from dotenv import load_dotenv
from gradio_client import Client, handle_file

# Add video generation imports
import whisperx
from pydub import AudioSegment, silence
import warnings

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Load environment variables from .env file
load_dotenv()

# Debug: Print OpenAI API key status
openai_key = os.getenv('OPENAI_API_KEY')
if openai_key:
    print(f"🔑 OpenAI API Key loaded: {openai_key[:10]}...{openai_key[-4:]}")
else:
    print("❌ OpenAI API Key not found in environment variables")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Voice Cloning Character Management API",
    description="API for managing characters, audio files, and images for video generation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
API_DATA_DIR = "apiData"
USER_PROFILES_FILE = os.path.join(API_DATA_DIR, "userProfiles.json")
SCRIPTS_FILE = os.path.join(API_DATA_DIR, "scripts.json")
AUDIO_FILES_DIR = os.path.join(API_DATA_DIR, "audio_files")
GENERATED_AUDIO_DIR = os.path.join(AUDIO_FILES_DIR, "generated")
IMAGES_DIR = os.path.join(API_DATA_DIR, "images")
BACKGROUND_DIR = os.path.join(API_DATA_DIR, "background")

# F5-TTS Configuration
F5TTS_URL = "http://localhost:7860"
F5TTS_TIMEOUT = 300  # 5 minutes

# Video Generation Configuration
VIDEO_OUTPUT_DIR = os.path.join(API_DATA_DIR, "video_output")
DEFAULT_BACKGROUND_VIDEO = "downloads/Minecraft Parkour Gameplay No Copyright_mobile.mp4"
FONT_PATH = 'C:/Windows/Fonts/impact.ttf'

# Ensure directories exist
os.makedirs(AUDIO_FILES_DIR, exist_ok=True)
os.makedirs(GENERATED_AUDIO_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(BACKGROUND_DIR, exist_ok=True)
os.makedirs(VIDEO_OUTPUT_DIR, exist_ok=True)

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Pydantic Models
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

class ScriptUpdate(BaseModel):
    dialogue: List[DialogueLine]

class AudioGenerationRequest(BaseModel):
    scriptId: str = Field(..., description="ID of the script to generate audio for")

class AudioGenerationStatus(BaseModel):
    scriptId: str
    status: str  # "pending", "processing", "completed", "failed"
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

# Video Generation Models
class VideoGenerationRequest(BaseModel):
    scriptId: str = Field(..., description="ID of the script to generate video for")
    backgroundVideo: Optional[str] = Field(None, description="Path to background video (optional)")

class VideoGenerationStatus(BaseModel):
    scriptId: str
    status: str  # "pending", "processing", "completed", "failed"
    stage: str  # Current processing stage
    progress: float  # Progress percentage (0-100)
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

# Utility Functions
def load_user_profiles() -> Dict[str, Any]:
    """Load user profiles from JSON file"""
    try:
        if os.path.exists(USER_PROFILES_FILE):
            with open(USER_PROFILES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Create default structure if file doesn't exist
            default_data = {
                "default": {
                    "speed": 1.0,
                    "nfeSteps": 34,
                    "crossFadeDuration": 0.15,
                    "removeSilences": True,
                    "f5ttsUrl": "http://localhost:7860",
                    "timeoutSeconds": 300,
                    "downloadDirectory": f"{API_DATA_DIR}/audio_files/generated",
                    "defaultAudioFile": f"{API_DATA_DIR}/audio_files/default.wav",
                    "defaultOutputPrefix": "defaultGenerated"
                },
                "users": {},
                "defaultUser": None,
                "createdAt": datetime.now().isoformat() + 'Z'
            }
            save_user_profiles(default_data)
            return default_data
    except Exception as e:
        logger.error(f"Error loading user profiles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to load user profiles: {str(e)}")

def save_user_profiles(data: Dict[str, Any]) -> None:
    """Save user profiles to JSON file"""
    try:
        # Ensure API data directory exists
        os.makedirs(API_DATA_DIR, exist_ok=True)
        
        with open(USER_PROFILES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info(f"User profiles saved to {USER_PROFILES_FILE}")
    except Exception as e:
        logger.error(f"Error saving user profiles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save user profiles: {str(e)}")

def generate_character_id(display_name: str) -> str:
    """Generate a unique character ID from display name"""
    # Create a base ID from display name (lowercase, remove spaces)
    base_id = display_name.lower().replace(' ', '').replace('-', '').replace('_', '')
    
    # Load existing profiles to check for conflicts
    profiles = load_user_profiles()
    existing_ids = set(profiles.get("users", {}).keys())
    
    # If no conflict, return base ID
    if base_id not in existing_ids:
        return base_id
    
    # If conflict, add number suffix
    counter = 1
    while f"{base_id}{counter}" in existing_ids:
        counter += 1
    
    return f"{base_id}{counter}"

def get_default_config() -> CharacterConfig:
    """Get default configuration from user profiles"""
    try:
        profiles = load_user_profiles()
        default_config = profiles.get("default", {})
        
        return CharacterConfig(
            speed=default_config.get("speed", 1.0),
            nfeSteps=default_config.get("nfeSteps", 34),
            crossFadeDuration=default_config.get("crossFadeDuration", 0.15),
            removeSilences=default_config.get("removeSilences", True)
        )
    except Exception as e:
        logger.warning(f"Could not load default config, using hardcoded defaults: {str(e)}")
        return CharacterConfig()

def validate_audio_file(file: UploadFile) -> bool:
    """Validate uploaded audio file"""
    # Check file extension
    allowed_extensions = {'.wav', '.mp3', '.m4a', '.flac', '.ogg'}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        return False
    
    # Check file size (max 50MB)
    if file.size and file.size > 50 * 1024 * 1024:
        return False
    
    return True

def validate_image_file(file: UploadFile) -> bool:
    """Validate uploaded image file"""
    # Check file extension
    allowed_extensions = {'.png', '.jpg', '.jpeg', '.webp'}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        return False
    
    # Check file size (max 10MB)
    if file.size and file.size > 10 * 1024 * 1024:
        return False
    
    return True

def load_scripts() -> Dict[str, Any]:
    """Load scripts from JSON file"""
    try:
        if os.path.exists(SCRIPTS_FILE):
            with open(SCRIPTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            default_data = {
                "scripts": {},
                "createdAt": datetime.now().isoformat()
            }
            save_scripts(default_data)
            return default_data
    except Exception as e:
        logger.error(f"Error loading scripts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to load scripts: {str(e)}")

def save_scripts(data: Dict[str, Any]) -> None:
    """Save scripts to JSON file"""
    try:
        os.makedirs(API_DATA_DIR, exist_ok=True)
        with open(SCRIPTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info(f"Scripts saved to {SCRIPTS_FILE}")
    except Exception as e:
        logger.error(f"Error saving scripts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save scripts: {str(e)}")

def generate_script_id() -> str:
    """Generate a unique script ID"""
    from datetime import datetime
    import uuid
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]
    return f"script_{timestamp}_{short_uuid}"

def generate_audio_filename(script_id: str, line_index: int, speaker: str) -> str:
    """Generate audio filename for a dialogue line"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_speaker = speaker.lower().replace(' ', '_').replace('-', '_')
    return f"{script_id}_line{line_index}_{safe_speaker}_{timestamp}.wav"

def check_f5tts_connection() -> bool:
    """Check if F5-TTS service is running"""
    try:
        response = requests.get(F5TTS_URL, timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"F5-TTS connection check failed: {str(e)}")
        return False

class F5TTSClient:
    """F5-TTS Gradio Client for audio generation"""
    
    def __init__(self, url: str = F5TTS_URL):
        self.url = url
        self.client = None
        
    def connect(self) -> bool:
        """Connect to F5-TTS Gradio API"""
        try:
            self.client = Client(self.url)
            logger.info(f"Connected to F5-TTS API: {self.url}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to F5-TTS API: {str(e)}")
            return False
    
    def generate_speech(self, audio_file_path: str, text: str, config: Dict[str, Any]) -> Optional[str]:
        """Generate speech using F5-TTS API"""
        if not self.client:
            logger.error("❌ Not connected to F5-TTS API")
            return None
        
        try:
            if not os.path.exists(audio_file_path):
                logger.error(f"❌ Audio file not found: {audio_file_path}")
                return None
            
            # Validate text
            if not text or not text.strip():
                logger.error("❌ Empty text provided for speech generation")
                return None
            
            text = text.strip()
            logger.info(f"🎤 F5-TTS generating speech for text: {text[:50]}...")
            
            start_time = time.time()
            
            # Call F5-TTS API with error handling
            result = self.client.predict(
                ref_audio_input=handle_file(os.path.abspath(audio_file_path)),
                ref_text_input="",  # Leave empty for auto-transcription
                gen_text_input=text,
                remove_silence=config.get("removeSilences", True),
                randomize_seed=True,
                seed_input=0,
                cross_fade_duration_slider=config.get("crossFadeDuration", 0.15),
                nfe_slider=int(config.get("nfeSteps", 34)),
                speed_slider=config.get("speed", 1.0),
                api_name="/basic_tts"
            )
            
            duration = time.time() - start_time
            
            # Validate result
            if result is None:
                logger.error("❌ F5-TTS returned None result")
                return None
            
            # Extract audio file path from result
            audio_path = None
            if isinstance(result, tuple) and len(result) > 0:
                audio_path = result[0]
            elif isinstance(result, str):
                audio_path = result
            else:
                logger.error(f"❌ Unexpected F5-TTS result format: {type(result)}")
                return None
            
            # Validate the returned audio file
            if not audio_path or not os.path.exists(audio_path):
                logger.error(f"❌ F5-TTS returned invalid audio path: {audio_path}")
                return None
            
            # Check file size
            file_size = os.path.getsize(audio_path)
            if file_size == 0:
                logger.error(f"❌ F5-TTS generated empty audio file: {audio_path}")
                return None
            
            logger.info(f"✅ F5-TTS speech generated successfully in {duration:.2f}s (size: {file_size} bytes)")
            return audio_path
                
        except Exception as e:
            logger.error(f"❌ F5-TTS generation failed: {str(e)}")
            return None
    
    def close(self):
        """Close the connection"""
        if self.client:
            self.client = None
            logger.info("F5-TTS API connection closed")

class VideoGenerator:
    """Video generation pipeline for scripts with audio"""
    
    def __init__(self):
        self.whisper_model = None
        self.align_model = None
        self.align_metadata = None
        
    def _initialize_whisper_models(self):
        """Initialize Whisper models for subtitle generation"""
        try:
            if self.whisper_model is None:
                logger.info("🎙️ Initializing Whisper models for subtitle generation...")
                device = "cpu"
                
                # Try to initialize WhisperX models
                try:
                    self.whisper_model = whisperx.load_model("base", device, compute_type="float32")
                    self.align_model, self.align_metadata = whisperx.load_align_model(
                        language_code="en",
                        device=device,
                        model_name="WAV2VEC2_ASR_LARGE_LV60K_960H"
                    )
                    logger.info("✅ Whisper models initialized successfully")
                except Exception as whisper_error:
                    logger.warning(f"⚠️ WhisperX initialization failed: {str(whisper_error)}")
                    logger.info("🔄 Falling back to simple subtitle generation...")
                    # Set models to None to indicate fallback mode
                    self.whisper_model = "fallback"
                    self.align_model = None
                    self.align_metadata = None
                    
        except Exception as e:
            logger.error(f"❌ Failed to initialize subtitle generation: {str(e)}")
            # Use fallback mode instead of raising exception
            logger.info("🔄 Using fallback subtitle generation mode...")
            self.whisper_model = "fallback"
            self.align_model = None
            self.align_metadata = None
    
    def _get_random_background_video(self) -> str:
        """Get a random background video from the background directory or default"""
        try:
            if os.path.exists(BACKGROUND_DIR):
                background_files = [f for f in os.listdir(BACKGROUND_DIR) 
                                  if f.startswith('background') and f.endswith('.mp4')]
                if background_files:
                    random_background = random.choice(background_files)
                    background_video = os.path.join(BACKGROUND_DIR, random_background)
                    logger.info(f"🎲 Randomly selected background: {random_background}")
                    return background_video
            
            # Fallback to default
            if os.path.exists(DEFAULT_BACKGROUND_VIDEO):
                logger.info(f"📺 Using default background video: {DEFAULT_BACKGROUND_VIDEO}")
                return DEFAULT_BACKGROUND_VIDEO
            else:
                raise Exception(f"No background video found. Default path: {DEFAULT_BACKGROUND_VIDEO}")
                
        except Exception as e:
            logger.error(f"❌ Error getting background video: {str(e)}")
            raise Exception(f"Background video error: {str(e)}")
    
    def _generate_subtitle_for_audio(self, audio_file: str, dialogue_text: str) -> Optional[Dict]:
        """Generate subtitle information for a single audio clip"""
        temp_audio_path = "temp_single_audio.wav"
        
        try:
            # Validate inputs
            if not audio_file or not dialogue_text:
                logger.error("❌ Missing audio file or dialogue text for subtitle generation")
                return None
            
            # Check if audio file exists
            if not os.path.exists(audio_file):
                logger.error(f"❌ Audio file not found: {audio_file}")
                return None
            
            logger.info(f"🎬 Generating subtitles for: {os.path.basename(audio_file)}")
            
            # Load audio to get duration
            try:
                audio = AudioSegment.from_file(audio_file)
                audio_duration = len(audio) / 1000.0  # Convert to seconds
            except Exception as e:
                logger.error(f"❌ Failed to process audio file {audio_file}: {str(e)}")
                return None
            
            # Check if we're in fallback mode or have proper WhisperX models
            if self.whisper_model == "fallback" or not self.align_model:
                logger.info("🔄 Using fallback subtitle generation (simple timing)")
                return self._generate_simple_subtitles(dialogue_text, audio_duration)
            
            # Copy audio file to temp location for WhisperX processing
            try:
                audio.export(temp_audio_path, format="wav")
            except Exception as e:
                logger.error(f"❌ Failed to export audio for WhisperX: {str(e)}")
                return self._generate_simple_subtitles(dialogue_text, audio_duration)
            
            # Transcribe with Whisper
            try:
                transcription = self.whisper_model.transcribe(
                    temp_audio_path,
                    batch_size=1,
                    language="en",
                    task="transcribe"
                )
                
                if not transcription.get("segments"):
                    logger.warning("❌ No segments found in transcription, using fallback")
                    return self._generate_simple_subtitles(dialogue_text, audio_duration)
                
            except Exception as e:
                logger.error(f"❌ Whisper transcription failed: {str(e)}, using fallback")
                return self._generate_simple_subtitles(dialogue_text, audio_duration)
            
            # Align words
            try:
                aligned_data = whisperx.align(
                    transcription["segments"],
                    self.align_model,
                    self.align_metadata,
                    temp_audio_path,
                    "cpu",
                    return_char_alignments=False
                )
                
                if not aligned_data.get("word_segments"):
                    logger.warning("❌ No word segments found in alignment, using fallback")
                    return self._generate_simple_subtitles(dialogue_text, audio_duration)
                
            except Exception as e:
                logger.error(f"❌ Word alignment failed: {str(e)}, using fallback")
                return self._generate_simple_subtitles(dialogue_text, audio_duration)
            
            # Parse original dialogue text into words
            try:
                import re
                original_words = []
                clean_line = re.sub(r'[^\w\s]', '', dialogue_text.strip())
                words = clean_line.split()
                original_words.extend(words)
                
                if not original_words:
                    logger.warning("❌ No words found in original dialogue, using fallback")
                    return self._generate_simple_subtitles(dialogue_text, audio_duration)
                
            except Exception as e:
                logger.error(f"❌ Failed to parse original dialogue: {str(e)}, using fallback")
                return self._generate_simple_subtitles(dialogue_text, audio_duration)
            
            # Create subtitle segments
            try:
                word_segments = aligned_data["word_segments"]
                subtitle_segments = []
                group_size = 4
                
                for i in range(0, len(word_segments), group_size):
                    group = word_segments[i:i+group_size]
                    start = group[0]['start']
                    end = group[-1]['end']
                    
                    # Use original words instead of Whisper transcribed words
                    group_words = []
                    for j, segment in enumerate(group):
                        original_index = i + j
                        if original_index < len(original_words):
                            group_words.append(original_words[original_index])
                        else:
                            group_words.append(segment['word'].strip())
                    
                    text = " ".join([w for w in group_words if w])
                    if text:  # Only add non-empty segments
                        subtitle_segments.append({
                            "start": start,
                            "end": end,
                            "text": text
                        })
                
                if not subtitle_segments:
                    logger.warning("❌ No subtitle segments created, using fallback")
                    return self._generate_simple_subtitles(dialogue_text, audio_duration)
                
                return {
                    "segments": subtitle_segments,
                    "duration": audio_duration
                }
                
            except Exception as e:
                logger.error(f"❌ Failed to create subtitle segments: {str(e)}, using fallback")
                return self._generate_simple_subtitles(dialogue_text, audio_duration)
            
        except Exception as e:
            logger.error(f"❌ Unexpected error generating subtitle: {str(e)}, using fallback")
            # Try to get audio duration if not already available
            try:
                if 'audio_duration' not in locals():
                    audio = AudioSegment.from_file(audio_file)
                    audio_duration = len(audio) / 1000.0
            except:
                audio_duration = 3.0  # Default fallback duration
            return self._generate_simple_subtitles(dialogue_text, audio_duration)
        finally:
            # Cleanup temp file
            try:
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
            except Exception as e:
                logger.warning(f"Warning: Failed to cleanup temp file {temp_audio_path}: {str(e)}")
    
    def _generate_simple_subtitles(self, dialogue_text: str, audio_duration: float) -> Dict:
        """Generate simple subtitles with basic timing when WhisperX is not available"""
        try:
            import re
            
            # Clean and split the dialogue text into words
            clean_text = re.sub(r'[^\w\s]', '', dialogue_text.strip())
            words = clean_text.split()
            
            if not words:
                # If no words, create a single subtitle for the entire duration
                return {
                    "segments": [{
                        "start": 0.0,
                        "end": audio_duration,
                        "text": dialogue_text.strip()
                    }],
                    "duration": audio_duration
                }
            
            # Create subtitle segments with simple timing
            subtitle_segments = []
            words_per_segment = 4  # Group words into segments of 4
            segment_duration = audio_duration / max(1, len(words) / words_per_segment)
            
            for i in range(0, len(words), words_per_segment):
                segment_words = words[i:i + words_per_segment]
                start_time = i / words_per_segment * segment_duration
                end_time = min(start_time + segment_duration, audio_duration)
                
                subtitle_segments.append({
                    "start": start_time,
                    "end": end_time,
                    "text": " ".join(segment_words)
                })
            
            logger.info(f"✅ Generated {len(subtitle_segments)} simple subtitle segments")
            return {
                "segments": subtitle_segments,
                "duration": audio_duration
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to generate simple subtitles: {str(e)}")
            # Return a single subtitle for the entire duration as last resort
            return {
                "segments": [{
                    "start": 0.0,
                    "end": audio_duration,
                    "text": dialogue_text.strip()
                }],
                "duration": audio_duration
            }
    
    def _create_timeline(self, script_data: Dict, user_profiles: Dict) -> Tuple[List[Dict], float]:
        """Create timeline for video generation"""
        try:
            dialogue_lines = script_data.get("dialogue", [])
            if not dialogue_lines:
                logger.error("❌ No dialogue lines found in script")
                return [], 0
            
            timeline = []
            current_time = 0
            skipped_count = 0
            
            logger.info(f"🎬 Creating timeline from {len(dialogue_lines)} dialogue lines...")
            
            for i, dialogue_line in enumerate(dialogue_lines):
                try:
                    speaker = dialogue_line.get("speaker", "").lower()
                    text = dialogue_line.get("text", "")
                    audio_file = dialogue_line.get("audioFile", "")
                    
                    # Validate dialogue line data
                    if not audio_file or not text or not speaker:
                        logger.warning(f"⚠️ Missing data for dialogue line {i}, skipping...")
                        skipped_count += 1
                        continue
                    
                    # Check if audio file exists
                    if not os.path.exists(audio_file):
                        logger.error(f"❌ Audio file not found for line {i}: {audio_file}")
                        skipped_count += 1
                        continue
                    
                    logger.info(f"Processing dialogue line {i}: {speaker} - {text[:30]}...")
                    
                    # Generate subtitle information for this clip
                    subtitle_info = self._generate_subtitle_for_audio(audio_file, text)
                    if not subtitle_info:
                        logger.error(f"❌ Failed to generate subtitle info for line {i}")
                        skipped_count += 1
                        continue
                    
                    # Get character image
                    character_image = self._get_character_image(speaker, user_profiles)
                    
                    timeline_item = {
                        "lineIndex": i,
                        "speaker": speaker,
                        "text": text,
                        "audioFile": audio_file,
                        "imageFile": character_image,
                        "startTime": current_time,
                        "endTime": current_time + subtitle_info["duration"],
                        "duration": subtitle_info["duration"],
                        "subtitleSegments": subtitle_info["segments"]
                    }
                    
                    timeline.append(timeline_item)
                    current_time += subtitle_info["duration"]
                    
                    logger.info(f"✅ Added line {i} to timeline (duration: {subtitle_info['duration']:.2f}s)")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing dialogue line {i}: {str(e)}")
                    skipped_count += 1
                    continue
            
            if not timeline:
                logger.error("❌ No valid timeline items created")
                return [], 0
            
            logger.info(f"✅ Timeline created with {len(timeline)} items (skipped {skipped_count}), total duration: {current_time:.2f}s")
            return timeline, current_time
            
        except Exception as e:
            logger.error(f"❌ Unexpected error creating timeline: {str(e)}")
            return [], 0
    
    def _get_character_image(self, speaker: str, user_profiles: Dict) -> str:
        """Get a random image for the character speaker"""
        try:
            users = user_profiles.get("users", {})
            if speaker not in users:
                logger.warning(f"⚠️ Speaker '{speaker}' not found in user profiles")
                return ""
            
            character_data = users[speaker]
            images = character_data.get("images", {})
            
            if not images:
                logger.warning(f"⚠️ No images found for speaker '{speaker}'")
                return ""
            
            # Get a random image
            image_paths = list(images.values())
            random_image = random.choice(image_paths)
            
            # Verify image exists
            if os.path.exists(random_image):
                logger.info(f"🖼️ Selected image for {speaker}: {os.path.basename(random_image)}")
                return random_image
            else:
                logger.warning(f"⚠️ Selected image file not found: {random_image}")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Error getting character image for {speaker}: {str(e)}")
            return ""
    
    def _concatenate_audio_files(self, timeline: List[Dict], output_path: str) -> bool:
        """Concatenate audio files from timeline"""
        try:
            if not timeline:
                logger.error("❌ No timeline provided for audio concatenation")
                return False
            
            logger.info(f"🎵 Concatenating {len(timeline)} audio files...")
            
            combined_audio = AudioSegment.empty()
            processed_count = 0
            
            for i, item in enumerate(timeline):
                try:
                    audio_file = item.get("audioFile", "")
                    if not audio_file or not os.path.exists(audio_file):
                        logger.warning(f"⚠️ Audio file not found in timeline item {i}, skipping...")
                        continue
                    
                    logger.info(f"Loading audio file {i+1}/{len(timeline)}: {os.path.basename(audio_file)}")
                    
                    # Load and add audio
                    audio = AudioSegment.from_file(audio_file)
                    
                    if len(audio) == 0:
                        logger.warning(f"⚠️ Audio file has zero duration: {audio_file}")
                        continue
                    
                    combined_audio += audio
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Error processing audio file {i}: {str(e)}")
                    continue
            
            if processed_count == 0:
                logger.error("❌ No audio files were successfully processed")
                return False
            
            # Export combined audio
            try:
                logger.info(f"💾 Exporting combined audio to: {output_path}")
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                combined_audio.export(output_path, format="wav")
                
                if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                    logger.error(f"❌ Combined audio file was not created properly: {output_path}")
                    return False
                
                logger.info(f"✅ Audio concatenation successful: {processed_count} files, duration: {len(combined_audio)/1000:.2f}s")
                return True
                
            except Exception as e:
                logger.error(f"❌ Failed to export combined audio: {str(e)}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Unexpected error in audio concatenation: {str(e)}")
            return False
    
    def _get_video_duration(self, video_path: str) -> float:
        """Get video duration using ffprobe"""
        try:
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', video_path
            ], capture_output=True, text=True, timeout=10)
            return float(result.stdout.strip()) if result.returncode == 0 else 3.0
        except Exception:
            return 3.0
    
    def _generate_video_with_ffmpeg(self, background_video: str, timeline: List[Dict], 
                                   total_duration: float, combined_audio: str, 
                                   output_video: str, script_id: str) -> bool:
        """Generate final video using FFmpeg"""
        try:
            logger.info(f"🎬 Generating video with FFmpeg...")
            logger.info(f"Background: {background_video}")
            logger.info(f"Audio: {combined_audio}")
            logger.info(f"Duration: {total_duration:.2f}s")
            logger.info(f"Output: {output_video}")
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_video), exist_ok=True)
            
            # Check font file
            font_path = FONT_PATH
            if not os.path.exists(font_path):
                logger.warning(f"⚠️ Font file not found: {font_path}, using default font")
                font_path = 'arial'  # Fallback to system default
            else:
                # Escape colons in Windows paths for FFmpeg
                font_path = font_path.replace(':', '\\:')
            
            # Build FFmpeg command
            filter_parts = []
            input_parts = ['-hwaccel', 'cuda', '-stream_loop', '-1', '-i', background_video, '-i', combined_audio]
            
            # Add image inputs and validate them
            image_inputs = {}
            valid_images = 0
            input_index = 2
            
            for item in timeline:
                image_file = item.get("imageFile", "")
                if image_file and os.path.exists(image_file):
                    input_parts.extend(['-i', image_file])
                    image_inputs[item["lineIndex"]] = input_index
                    input_index += 1
                    valid_images += 1
                    logger.info(f"✅ Added image for line {item['lineIndex']}: {os.path.basename(image_file)}")
                else:
                    logger.warning(f"⚠️ No valid image for line {item['lineIndex']}: {image_file}")
            
            logger.info(f"Added {valid_images} valid images out of {len(timeline)} timeline items")
            
            # Build filter complex
            try:
                # Background video processing
                filter_parts.append(f"[0:v]scale=1080:1920:force_original_aspect_ratio=disable,setsar=1,trim=duration={total_duration},setpts=PTS-STARTPTS[bg]")
                current_base = "[bg]"
                
                # Add overlays and subtitles
                overlay_count = 0
                subtitle_count = 0
                
                for item in timeline:
                    line_index = item.get("lineIndex", 0)
                    
                    # Add image overlay if available
                    if line_index in image_inputs:
                        img_input = image_inputs[line_index]
                        filter_parts.append(
                            f"{current_base}[{img_input}:v]overlay=0:0:enable='between(t,{item['startTime']},{item['endTime']})'[overlay{overlay_count}]"
                        )
                        current_base = f"[overlay{overlay_count}]"
                        overlay_count += 1
                    
                    # Add subtitles for this segment
                    if "subtitleSegments" in item and item["subtitleSegments"]:
                        for segment in item["subtitleSegments"]:
                            start = item["startTime"] + segment["start"]
                            end = item["startTime"] + segment["end"]
                            text = segment.get("text", "").strip()
                            
                            if not text:
                                continue
                                
                            # Escape special characters in text for FFmpeg
                            text = text.replace("'", "\\'").replace('"', '\\"').replace(':', '\\:')
                            
                            filter_parts.append(
                                f"{current_base}drawtext=text='{text}':fontfile='{font_path}':fontsize=64:borderw=3:bordercolor=black:fontcolor=white:x=(w-text_w)/2:y=h-th-150:enable='between(t,{start:.3f},{end:.3f})'[sub{subtitle_count}]"
                            )
                            current_base = f"[sub{subtitle_count}]"
                            subtitle_count += 1
                
                logger.info(f"Added {overlay_count} overlays and {subtitle_count} subtitle segments")
                
                # Final output (simplified - no main title for now)
                filter_parts.append(f"{current_base}setpts=PTS-STARTPTS[final_video]")
                output_mapping = ['-map', '[final_video]', '-map', '1:a']
                
            except Exception as e:
                logger.error(f"❌ Error building FFmpeg filters: {str(e)}")
                return False
            
            # Build final FFmpeg command
            try:
                filter_complex = ";".join(filter_parts)
                
                # Debug: Log the filter complex (truncated for readability)
                if len(filter_complex) > 500:
                    logger.info(f"Filter complex (first 500 chars): {filter_complex[:500]}...")
                else:
                    logger.info(f"Filter complex: {filter_complex}")
                
                cmd = [
                    'ffmpeg', '-y',
                    *input_parts,
                    '-filter_complex', filter_complex,
                    *output_mapping,
                    '-c:v', 'h264_nvenc',
                    '-preset', 'fast',
                    '-c:a', 'aac',
                    '-shortest',
                    output_video
                ]
                
                logger.info("Executing FFmpeg command...")
                logger.info(f"FFmpeg inputs: {len([x for x in input_parts if not x.startswith('-')])} files")
                
            except Exception as e:
                logger.error(f"❌ Error building FFmpeg command: {str(e)}")
                return False
            
            # Execute FFmpeg
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)  # 10 minute timeout
                
                if result.returncode != 0:
                    logger.error(f"❌ FFmpeg failed with return code: {result.returncode}")
                    logger.error(f"FFmpeg stderr: {result.stderr}")
                    return False
                
                # Verify output file was created
                if not os.path.exists(output_video) or os.path.getsize(output_video) == 0:
                    logger.error(f"❌ Output video file was not created properly: {output_video}")
                    return False
                
                file_size = os.path.getsize(output_video)
                logger.info(f"✅ FFmpeg video generation successful!")
                logger.info(f"Output file: {output_video}")
                logger.info(f"File size: {file_size} bytes")
                
                return True
                
            except subprocess.TimeoutExpired:
                logger.error("❌ FFmpeg process timed out (10 minutes)")
                return False
            except Exception as e:
                logger.error(f"❌ Error executing FFmpeg: {str(e)}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Unexpected error in video generation: {str(e)}")
            return False
    
    async def generate_video(self, script_id: str, background_video: Optional[str] = None) -> VideoGenerationResponse:
        """Main video generation pipeline"""
        try:
            logger.info(f"🎬 Starting video generation for script: {script_id}")
            
            # Load script data
            scripts_data = load_scripts()
            scripts = scripts_data.get("scripts", {})
            
            if script_id not in scripts:
                raise HTTPException(status_code=404, detail=f"Script '{script_id}' not found")
            
            script_data = scripts[script_id]
            dialogue_lines = script_data.get("dialogue", [])
            
            if not dialogue_lines:
                raise HTTPException(status_code=400, detail="Script has no dialogue lines")
            
            # Check if all dialogue lines have audio
            missing_audio = []
            for i, line in enumerate(dialogue_lines):
                audio_file = line.get("audioFile", "")
                if not audio_file or not os.path.exists(audio_file):
                    missing_audio.append(i)
            
            if missing_audio:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Audio files missing for dialogue lines: {missing_audio}. Generate audio first."
                )
            
            # Initialize Whisper models
            logger.info("🎙️ Initializing Whisper models...")
            self._initialize_whisper_models()
            
            # Get background video
            if not background_video:
                background_video = self._get_random_background_video()
            
            if not os.path.exists(background_video):
                raise HTTPException(status_code=400, detail=f"Background video not found: {background_video}")
            
            # Load user profiles for character images
            user_profiles = load_user_profiles()
            
            # Create timeline
            logger.info("🎬 Creating timeline...")
            timeline, total_duration = self._create_timeline(script_data, user_profiles)
            
            if not timeline:
                raise HTTPException(status_code=500, detail="Failed to create timeline - no valid segments")
            
            logger.info(f"Created timeline with {len(timeline)} segments, total duration: {total_duration:.2f}s")
            
            # Concatenate audio
            logger.info("🎵 Concatenating audio files...")
            combined_audio_path = os.path.join(VIDEO_OUTPUT_DIR, f"{script_id}_combined_audio.wav")
            
            if not self._concatenate_audio_files(timeline, combined_audio_path):
                raise HTTPException(status_code=500, detail="Failed to concatenate audio files")
            
            # Generate final video
            logger.info("🎬 Generating final video...")
            final_video_path = os.path.join(VIDEO_OUTPUT_DIR, f"{script_id}_final_video.mp4")
            
            if not self._generate_video_with_ffmpeg(
                background_video, timeline, total_duration, combined_audio_path, final_video_path, script_id
            ):
                raise HTTPException(status_code=500, detail="FFmpeg video generation failed")
            
            # Update script with final video path
            script_data["finalVideoPath"] = final_video_path
            script_data["videoDuration"] = total_duration
            script_data["updatedAt"] = datetime.now().isoformat()
            scripts[script_id] = script_data
            save_scripts(scripts_data)
            
            # Cleanup temp files
            try:
                if os.path.exists(combined_audio_path):
                    os.remove(combined_audio_path)
                    logger.info(f"Cleaned up temp file: {combined_audio_path}")
            except Exception as e:
                logger.warning(f"Warning: Failed to cleanup temp file: {str(e)}")
            
            logger.info(f"✅ Video generation completed successfully for script: {script_id}")
            
            return VideoGenerationResponse(
                scriptId=script_id,
                status="completed",
                message=f"✅ Video generated successfully with {len(timeline)} segments",
                finalVideoPath=final_video_path,
                duration=total_duration
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Video generation failed for script {script_id}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")

def get_openai_client():
    """Get OpenAI client - you'll need to set OPENAI_API_KEY environment variable"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.")
    return OpenAI(api_key=api_key)

def load_script_generation_prompt() -> str:
    """Load the script generation prompt from prompts.py"""
    try:
        # Import the prompt from src/prompts.py
        import sys
        sys.path.append('src')
        from prompts import SCRIPT_GENERATION_PROMPT
        return SCRIPT_GENERATION_PROMPT
    except ImportError as e:
        logger.error(f"Could not import prompts: {str(e)}")
        # Fallback prompt if prompts.py is not available
        return """
You are an expert dialogue scriptwriter specializing in political satire and educational content.

Your task is to create engaging, witty, and insightful dialogue scripts that bring complex topics to life through character interactions.

Selected Characters: {characters}
Topic/Situation: {topic}

Additional Context: {additional_context}

Generate a natural, engaging dialogue between these characters about the given topic. Format output as: {{Character}} their dialogue line
"""

async def generate_audio_for_script(script_id: str) -> AudioGenerationResponse:
    """Generate audio files for all dialogue lines in a script"""
    try:
        # Load script data
        scripts_data = load_scripts()
        scripts = scripts_data.get("scripts", {})
        
        if script_id not in scripts:
            raise HTTPException(status_code=404, detail=f"Script '{script_id}' not found")
        
        script = scripts[script_id]
        dialogue_lines = script.get("dialogue", [])
        
        if not dialogue_lines:
            raise HTTPException(status_code=400, detail="Script has no dialogue lines")
        
        # Check F5-TTS connection
        if not check_f5tts_connection():
            raise HTTPException(status_code=503, detail="F5-TTS service is not available")
        
        # Load user profiles to get character audio files and configs
        profiles = load_user_profiles()
        users = profiles.get("users", {})
        
        # Initialize F5-TTS client
        f5tts_client = F5TTSClient()
        if not f5tts_client.connect():
            raise HTTPException(status_code=503, detail="Failed to connect to F5-TTS service")
        
        try:
            total_lines = len(dialogue_lines)
            processed_lines = 0
            completed_lines = 0
            failed_lines = 0
            
            logger.info(f"Starting audio generation for script {script_id} with {total_lines} lines")
            
            # Create a copy of dialogue lines to modify
            updated_dialogue = []
            
            for line_index, dialogue_line in enumerate(dialogue_lines):
                try:
                    speaker = dialogue_line.get("speaker", "").lower()
                    text = dialogue_line.get("text", "").strip()
                    existing_audio = dialogue_line.get("audioFile", "")
                    
                    logger.info(f"Processing line {line_index}: {speaker} - {text[:30]}...")
                    
                    # Create the dialogue line object (start with original data)
                    updated_line = {
                        "speaker": dialogue_line.get("speaker", ""),
                        "text": text,
                        "audioFile": existing_audio if existing_audio else ""
                    }
                    
                    # Skip if missing speaker or text
                    if not speaker or not text:
                        logger.warning(f"❌ Skipping line {line_index}: missing speaker or text")
                        failed_lines += 1
                        processed_lines += 1
                        updated_dialogue.append(updated_line)
                        continue
                    
                    # Skip if audio already exists and is valid
                    if existing_audio and existing_audio.strip() and os.path.exists(existing_audio):
                        logger.info(f"✅ Audio already exists for line {line_index}, skipping generation: {existing_audio}")
                        completed_lines += 1
                        processed_lines += 1
                        updated_dialogue.append(updated_line)
                        continue
                    
                    # Clear any invalid existing audio path
                    if existing_audio and existing_audio.strip() and not os.path.exists(existing_audio):
                        logger.warning(f"⚠️ Invalid audio path found for line {line_index}, will regenerate: {existing_audio}")
                        updated_line["audioFile"] = ""
                    
                    # Validate character exists
                    if speaker not in users:
                        logger.error(f"❌ Character '{speaker}' not found in user profiles")
                        failed_lines += 1
                        processed_lines += 1
                        updated_dialogue.append(updated_line)
                        continue
                    
                    char_data = users[speaker]
                    char_audio_file = char_data.get("audioFile", "")
                    
                    # Validate character audio file exists
                    if not char_audio_file or not os.path.exists(char_audio_file):
                        logger.error(f"❌ Audio file not found for character '{speaker}': {char_audio_file}")
                        failed_lines += 1
                        processed_lines += 1
                        updated_dialogue.append(updated_line)
                        continue
                    
                    # Get character config
                    char_config = char_data.get("config", {})
                    
                    # Generate filename for output
                    output_filename = generate_audio_filename(script_id, line_index, speaker)
                    output_path = os.path.join(GENERATED_AUDIO_DIR, output_filename)
                    
                    logger.info(f"🎤 Generating audio for line {line_index}: {speaker} - {text[:50]}...")
                    
                    # Attempt to generate speech
                    try:
                        temp_audio_path = f5tts_client.generate_speech(char_audio_file, text, char_config)
                        
                        if temp_audio_path and os.path.exists(temp_audio_path):
                            # Copy to our managed location
                            try:
                                shutil.copy2(temp_audio_path, output_path)
                                
                                # Verify the file was copied successfully and has content
                                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                                    updated_line["audioFile"] = output_path
                                    completed_lines += 1
                                    logger.info(f"✅ Audio generated successfully for line {line_index}: {output_filename}")
                                else:
                                    logger.error(f"❌ Audio file copy failed or empty for line {line_index}")
                                    # Clean up empty file if it exists
                                    if os.path.exists(output_path):
                                        try:
                                            os.remove(output_path)
                                        except:
                                            pass
                                    failed_lines += 1
                            except Exception as copy_error:
                                logger.error(f"❌ Failed to copy audio file for line {line_index}: {str(copy_error)}")
                                failed_lines += 1
                        else:
                            logger.error(f"❌ F5-TTS generation failed for line {line_index} - no valid audio returned")
                            failed_lines += 1
                            
                    except Exception as gen_error:
                        logger.error(f"❌ Audio generation error for line {line_index}: {str(gen_error)}")
                        failed_lines += 1
                    
                    processed_lines += 1
                    updated_dialogue.append(updated_line)
                    
                except Exception as e:
                    logger.error(f"❌ Unexpected error processing line {line_index}: {str(e)}")
                    failed_lines += 1
                    processed_lines += 1
                    # Add the original line without any audio file on error
                    updated_dialogue.append({
                        "speaker": dialogue_line.get("speaker", ""),
                        "text": dialogue_line.get("text", ""),
                        "audioFile": ""  # Clear audio file on error
                    })
                    continue
            
            # Update script with modified dialogue
            script["dialogue"] = updated_dialogue
            script["updatedAt"] = datetime.now().isoformat()
            scripts[script_id] = script
            save_scripts(scripts_data)
            logger.info(f"Updated script {script_id} with {completed_lines} audio files in dialogue array")
            
            # Log summary
            logger.info(f"📊 Audio Generation Summary for {script_id}:")
            logger.info(f"   Total Lines: {total_lines}")
            logger.info(f"   Processed: {processed_lines}")
            logger.info(f"   Completed: {completed_lines}")
            logger.info(f"   Failed: {failed_lines}")
            logger.info(f"   Skipped (already had audio): {total_lines - processed_lines}")
            
            # Determine final status
            if completed_lines == total_lines:
                status = "completed"
                message = f"✅ Successfully generated audio for all {completed_lines} dialogue lines"
            elif completed_lines > 0:
                status = "partial"
                message = f"⚠️ Generated audio for {completed_lines}/{total_lines} lines ({failed_lines} failed)"
            else:
                status = "failed"
                message = f"❌ Failed to generate audio for any lines ({failed_lines} failures)"
            
            logger.info(f"🎯 Audio generation completed for script {script_id}: {message}")
            print(f"🎯 Audio generation completed for script {script_id}: {message}")
            
            return AudioGenerationResponse(
                scriptId=script_id,
                status=status,
                message=message,
                completedLines=completed_lines,
                totalLines=total_lines
            )
            
        finally:
            f5tts_client.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in audio generation for script {script_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Audio generation failed: {str(e)}")

async def generate_script_with_openai(selected_characters: List[str], prompt: str, word: Optional[str] = None) -> List[DialogueLine]:
    """Generate script using OpenAI API"""
    try:
        client = get_openai_client()
        
        # Load the script generation prompt
        script_prompt_template = load_script_generation_prompt()
        
        # Prepare the topic and additional context
        if word:
            topic = f"Explaining the concept/word: {word}"
            additional_context = f"User's situation/context: {prompt}"
        else:
            topic = prompt
            additional_context = "Focus on creating an engaging dialogue that explores this topic naturally."
        
        # Format the system prompt with the template
        system_prompt = script_prompt_template.format(
            characters=', '.join(selected_characters),
            topic=topic,
            additional_context=additional_context
        )
        
        # Create user prompt for additional guidance
        user_prompt = f"""
Create a dialogue script for the following:

Characters: {', '.join(selected_characters)}
Topic: {topic}
Context: {additional_context}

Remember to:
- Keep each character true to their personality
- Make the dialogue natural and engaging
- Format each line as: {{Character}} their dialogue
- Keep it concise (4-6 lines total)
"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.8
        )
        
        # Parse the response
        script_text = response.choices[0].message.content.strip()
        dialogue_lines = []
        
        # Parse the script format: {{Character}} dialogue text
        for line in script_text.split('\n'):
            line = line.strip()
            if line and '{{' in line and '}}' in line:
                # Extract character name and dialogue
                start_idx = line.find('{{') + 2
                end_idx = line.find('}}')
                if start_idx > 1 and end_idx > start_idx:
                    character = line[start_idx:end_idx].strip()
                    dialogue_text = line[end_idx + 2:].strip()
                    
                    # Clean up character name (remove any extra formatting)
                    character = character.replace('{{', '').replace('}}', '')
                    
                    if character and dialogue_text:
                        dialogue_lines.append(DialogueLine(speaker=character, text=dialogue_text))
        
        if not dialogue_lines:
            # Fallback parsing if the format is different
            lines = script_text.split('\n')
            for line in lines:
                line = line.strip()
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        character = parts[0].strip()
                        dialogue_text = parts[1].strip()
                        if character and dialogue_text:
                            dialogue_lines.append(DialogueLine(speaker=character, text=dialogue_text))
        
        if not dialogue_lines:
            raise HTTPException(status_code=500, detail="Failed to parse generated script")
        
        return dialogue_lines
        
    except Exception as e:
        logger.error(f"Error generating script with OpenAI: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate script: {str(e)}")

# API Endpoints

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/system/status", response_model=SystemStatus)
async def get_system_status():
    """Get system status and statistics"""
    try:
        profiles = load_user_profiles()
        total_characters = len(profiles.get("users", {}))
        
        return SystemStatus(
            status="active",
            totalCharacters=total_characters,
            timestamp=datetime.now().isoformat(),
            apiDataDir=os.path.abspath(API_DATA_DIR)
        )
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/characters", response_model=List[CharacterResponse])
async def list_characters():
    """List all characters"""
    try:
        profiles = load_user_profiles()
        users = profiles.get("users", {})
        
        characters = []
        for char_id, char_data in users.items():
            # Check if audio file exists
            audio_file = char_data.get("audioFile", "")
            has_audio = bool(audio_file and os.path.exists(audio_file))
            
            # Count images
            images = char_data.get("images", {})
            image_count = len(images)
            
            # Get config with defaults
            config_data = char_data.get("config", {})
            default_config = get_default_config()
            
            config = CharacterConfig(
                speed=config_data.get("speed", default_config.speed),
                nfeSteps=config_data.get("nfeSteps", default_config.nfeSteps),
                crossFadeDuration=config_data.get("crossFadeDuration", default_config.crossFadeDuration),
                removeSilences=config_data.get("removeSilences", default_config.removeSilences)
            )
            
            character = CharacterResponse(
                id=char_id,
                displayName=char_data.get("displayName", char_id.title()),
                audioFile=audio_file,
                config=config,
                images=images,
                outputPrefix=char_data.get("outputPrefix", char_id),
                createdAt=char_data.get("createdAt", datetime.now().isoformat()),
                updatedAt=char_data.get("updatedAt", datetime.now().isoformat()),
                hasAudio=has_audio,
                imageCount=image_count
            )
            characters.append(character)
        
        return characters
    except Exception as e:
        logger.error(f"Error listing characters: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/characters/{character_id}", response_model=CharacterResponse)
async def get_character(character_id: str):
    """Get a specific character by ID"""
    try:
        profiles = load_user_profiles()
        users = profiles.get("users", {})
        
        if character_id not in users:
            raise HTTPException(status_code=404, detail=f"Character '{character_id}' not found")
        
        char_data = users[character_id]
        
        # Check if audio file exists
        audio_file = char_data.get("audioFile", "")
        has_audio = bool(audio_file and os.path.exists(audio_file))
        
        # Count images
        images = char_data.get("images", {})
        image_count = len(images)
        
        # Get config with defaults
        config_data = char_data.get("config", {})
        default_config = get_default_config()
        
        config = CharacterConfig(
            speed=config_data.get("speed", default_config.speed),
            nfeSteps=config_data.get("nfeSteps", default_config.nfeSteps),
            crossFadeDuration=config_data.get("crossFadeDuration", default_config.crossFadeDuration),
            removeSilences=config_data.get("removeSilences", default_config.removeSilences)
        )
        
        return CharacterResponse(
            id=character_id,
            displayName=char_data.get("displayName", character_id.title()),
            audioFile=audio_file,
            config=config,
            images=images,
            outputPrefix=char_data.get("outputPrefix", character_id),
            createdAt=char_data.get("createdAt", datetime.now().isoformat()),
            updatedAt=char_data.get("updatedAt", datetime.now().isoformat()),
            hasAudio=has_audio,
            imageCount=image_count
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting character {character_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/characters/{character_id}", response_model=CharacterResponse)
async def update_character(character_id: str, updates: CharacterUpdate):
    """Update an existing character"""
    try:
        profiles = load_user_profiles()
        users = profiles.get("users", {})
        
        if character_id not in users:
            raise HTTPException(status_code=404, detail=f"Character '{character_id}' not found")
        
        char_data = users[character_id]
        current_time = datetime.now().isoformat()
        
        # Update display name if provided
        if updates.displayName is not None:
            char_data["displayName"] = updates.displayName
        
        # Update config if provided
        if updates.config is not None:
            char_data["config"] = {
                "speed": updates.config.speed,
                "nfeSteps": updates.config.nfeSteps,
                "crossFadeDuration": updates.config.crossFadeDuration,
                "removeSilences": updates.config.removeSilences
            }
        
        # Update timestamp
        char_data["updatedAt"] = current_time
        
        # Save profiles
        save_user_profiles(profiles)
        
        logger.info(f"Updated character: {character_id}")
        
        # Return updated character
        return await get_character(character_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating character {character_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/characters/{character_id}")
async def delete_character(character_id: str):
    """Delete a character and associated files"""
    try:
        profiles = load_user_profiles()
        users = profiles.get("users", {})
        
        if character_id not in users:
            raise HTTPException(status_code=404, detail=f"Character '{character_id}' not found")
        
        char_data = users[character_id]
        
        # Delete associated files
        deleted_files = []
        
        # Delete audio file
        audio_file = char_data.get("audioFile", "")
        if audio_file and os.path.exists(audio_file):
            try:
                os.remove(audio_file)
                deleted_files.append(audio_file)
                logger.info(f"Deleted audio file: {audio_file}")
            except Exception as e:
                logger.warning(f"Could not delete audio file {audio_file}: {str(e)}")
        
        # Delete image files
        images = char_data.get("images", {})
        for image_path in images.values():
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    deleted_files.append(image_path)
                    logger.info(f"Deleted image file: {image_path}")
                except Exception as e:
                    logger.warning(f"Could not delete image file {image_path}: {str(e)}")
        
        # Remove from profiles
        del profiles["users"][character_id]
        
        # Update default user if it was the deleted character
        if profiles.get("defaultUser") == character_id:
            remaining_users = list(profiles["users"].keys())
            profiles["defaultUser"] = remaining_users[0] if remaining_users else None
        
        # Save profiles
        save_user_profiles(profiles)
        
        logger.info(f"Deleted character: {character_id}")
        
        return {
            "message": f"Character '{character_id}' deleted successfully",
            "deletedFiles": deleted_files
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting character {character_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/characters/complete", response_model=CharacterResponse)
async def create_complete_character(
    displayName: str = Form(...),
    speed: Optional[float] = Form(None),
    nfeSteps: Optional[int] = Form(None),
    crossFadeDuration: Optional[float] = Form(None),
    removeSilences: Optional[bool] = Form(True),
    audioFile: UploadFile = File(...),
    imageFiles: List[UploadFile] = File(...)
):
    """Create a complete character with all data in one request"""
    try:
        logger.info(f"Creating complete character: {displayName}")
        
        if not displayName or len(displayName.strip()) == 0:
            raise HTTPException(status_code=400, detail="Display name is required")
        
        displayName = displayName.strip()
        character_id = generate_character_id(displayName)
        
        if not validate_audio_file(audioFile):
            raise HTTPException(
                status_code=400, 
                detail="Invalid audio file. Supported formats: WAV, MP3, M4A, FLAC, OGG. Max size: 50MB"
            )
        
        if len(imageFiles) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 images allowed per character")
        
        valid_images = []
        for img in imageFiles:
            if validate_image_file(img):
                valid_images.append(img)
            else:
                logger.warning(f"Skipping invalid image file: {img.filename}")
        
        if not valid_images:
            raise HTTPException(status_code=400, detail="At least one valid image is required")
        
        default_config = get_default_config()
        config = CharacterConfig(
            speed=speed if speed is not None else default_config.speed,
            nfeSteps=nfeSteps if nfeSteps is not None else default_config.nfeSteps,
            crossFadeDuration=crossFadeDuration if crossFadeDuration is not None else default_config.crossFadeDuration,
            removeSilences=removeSilences if removeSilences is not None else default_config.removeSilences
        )
        
        audio_extension = Path(audioFile.filename).suffix.lower()
        audio_filename = f"{character_id}{audio_extension}"
        audio_path = os.path.join(AUDIO_FILES_DIR, audio_filename)
        
        try:
            with open(audio_path, "wb") as buffer:
                shutil.copyfileobj(audioFile.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save audio file: {str(e)}")
        
        images_dict = {}
        uploaded_images = []
        
        for index, img in enumerate(valid_images):
            try:
                image_extension = Path(img.filename).suffix.lower()
                image_filename = f"{character_id}_{index}{image_extension}"
                image_path = os.path.join(IMAGES_DIR, image_filename)
                
                with open(image_path, "wb") as buffer:
                    shutil.copyfileobj(img.file, buffer)
                
                images_dict[str(index)] = image_path
                uploaded_images.append(image_path)
                
            except Exception as e:
                logger.error(f"Error saving image {index}: {str(e)}")
                continue
        
        if not images_dict:
            try:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
            except:
                pass
            raise HTTPException(status_code=500, detail="Failed to save any image files")
        
        current_time = datetime.now().isoformat()
        char_data = {
            "displayName": displayName,
            "audioFile": audio_path,
            "config": {
                "speed": config.speed,
                "nfeSteps": config.nfeSteps,
                "crossFadeDuration": config.crossFadeDuration,
                "removeSilences": config.removeSilences
            },
            "images": images_dict,
            "outputPrefix": character_id,
            "createdAt": current_time,
            "updatedAt": current_time
        }
        
        try:
            profiles = load_user_profiles()
            
            if "users" not in profiles:
                profiles["users"] = {}
            
            profiles["users"][character_id] = char_data
            save_user_profiles(profiles)
            logger.info(f"Created complete character: {character_id} ({displayName})")
            
        except Exception as e:
            try:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                for img_path in uploaded_images:
                    if os.path.exists(img_path):
                        os.remove(img_path)
            except:
                pass
            raise HTTPException(status_code=500, detail=f"Failed to save character data: {str(e)}")
        
        return CharacterResponse(
            id=character_id,
            displayName=displayName,
            audioFile=audio_path,
            config=config,
            images=images_dict,
            outputPrefix=character_id,
            createdAt=current_time,
            updatedAt=current_time,
            hasAudio=True,
            imageCount=len(images_dict)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating complete character: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# Script Management Endpoints

@app.post("/api/scripts/generate", response_model=ScriptResponse)
async def generate_script(request: ScriptRequest):
    """Generate a new script using OpenAI API"""
    try:
        logger.info(f"Generating script for characters: {request.selectedCharacters}")
        
        # Validate that selected characters exist
        profiles = load_user_profiles()
        users = profiles.get("users", {})
        
        for char_id in request.selectedCharacters:
            if char_id not in users:
                raise HTTPException(status_code=400, detail=f"Character '{char_id}' not found")
        
        # Generate script using OpenAI
        dialogue_lines = await generate_script_with_openai(
            request.selectedCharacters, 
            request.prompt, 
            request.word
        )
        
        # Create script data
        script_id = generate_script_id()
        current_time = datetime.now().isoformat()
        
        script_data = {
            "id": script_id,
            "selectedCharacters": request.selectedCharacters,
            "originalPrompt": request.prompt,
            "word": request.word,
            "dialogue": [{"speaker": line.speaker, "text": line.text, "audioFile": ""} for line in dialogue_lines],
            "createdAt": current_time,
            "updatedAt": current_time
        }
        
        # Save script
        scripts = load_scripts()
        scripts["scripts"][script_id] = script_data
        save_scripts(scripts)
        
        logger.info(f"Generated script: {script_id}")
        
        return ScriptResponse(
            id=script_data["id"],
            selectedCharacters=script_data["selectedCharacters"],
            originalPrompt=script_data["originalPrompt"],
            word=script_data.get("word"),
            dialogue=script_data["dialogue"],
            createdAt=script_data["createdAt"],
            updatedAt=script_data["updatedAt"],
            hasAudio=False,
            audioCount=0,
            finalVideoPath=None,
            videoDuration=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating script: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate script: {str(e)}")

@app.get("/api/scripts", response_model=List[ScriptResponse])
async def list_scripts():
    """List all scripts"""
    try:
        scripts_data = load_scripts()
        scripts = scripts_data.get("scripts", {})
        
        script_responses = []
        for script_data in scripts.values():
            dialogue_lines = script_data.get("dialogue", [])
            
            # Count lines with valid audio files
            audio_count = 0
            for dialogue_line in dialogue_lines:
                audio_file = dialogue_line.get("audioFile", "")
                if audio_file and os.path.exists(audio_file):
                    audio_count += 1
            
            script_response = ScriptResponse(
                id=script_data["id"],
                selectedCharacters=script_data["selectedCharacters"],
                originalPrompt=script_data["originalPrompt"],
                word=script_data.get("word"),
                dialogue=dialogue_lines,
                createdAt=script_data["createdAt"],
                updatedAt=script_data["updatedAt"],
                hasAudio=audio_count > 0,
                audioCount=audio_count,
                finalVideoPath=script_data.get("finalVideoPath"),
                videoDuration=script_data.get("videoDuration")
            )
            script_responses.append(script_response)
        
        return script_responses
        
    except Exception as e:
        logger.error(f"Error listing scripts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scripts/{script_id}", response_model=ScriptResponse)
async def get_script(script_id: str):
    """Get a specific script"""
    try:
        scripts_data = load_scripts()
        scripts = scripts_data.get("scripts", {})
        
        if script_id not in scripts:
            raise HTTPException(status_code=404, detail=f"Script '{script_id}' not found")
        
        script_data = scripts[script_id]
        dialogue_lines = script_data.get("dialogue", [])
        
        # Count lines with valid audio files
        audio_count = 0
        for dialogue_line in dialogue_lines:
            audio_file = dialogue_line.get("audioFile", "")
            if audio_file and os.path.exists(audio_file):
                audio_count += 1
        
        return ScriptResponse(
            id=script_data["id"],
            selectedCharacters=script_data["selectedCharacters"],
            originalPrompt=script_data["originalPrompt"],
            word=script_data.get("word"),
            dialogue=dialogue_lines,
            createdAt=script_data["createdAt"],
            updatedAt=script_data["updatedAt"],
            hasAudio=audio_count > 0,
            audioCount=audio_count,
            finalVideoPath=script_data.get("finalVideoPath"),
            videoDuration=script_data.get("videoDuration")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting script {script_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/scripts/{script_id}", response_model=ScriptResponse)
async def update_script(script_id: str, updates: ScriptUpdate):
    """Update a script's dialogue and handle audio cleanup for changed lines"""
    try:
        scripts_data = load_scripts()
        scripts = scripts_data.get("scripts", {})
        
        if script_id not in scripts:
            raise HTTPException(status_code=404, detail=f"Script '{script_id}' not found")
        
        script_data = scripts[script_id]
        old_dialogue = script_data.get("dialogue", [])
        new_dialogue_updates = updates.dialogue
        
        logger.info(f"Updating script {script_id} with {len(new_dialogue_updates)} dialogue lines")
        
        # Process each dialogue line and handle audio cleanup
        updated_dialogue = []
        deleted_audio_files = []
        dialogue_changed = False
        
        for i, new_line in enumerate(new_dialogue_updates):
            # Get the old line if it exists
            old_line = old_dialogue[i] if i < len(old_dialogue) else None
            
            # Create the new dialogue line structure
            new_dialogue_line = {
                "speaker": new_line.speaker,
                "text": new_line.text,
                "audioFile": ""  # Start with empty audio file
            }
            
            # Check if this line existed before and had audio
            if old_line:
                old_text = old_line.get("text", "").strip()
                old_speaker = old_line.get("speaker", "").strip()
                old_audio = old_line.get("audioFile", "")
                
                new_text = new_line.text.strip()
                new_speaker = new_line.speaker.strip()
                
                # Check if the line content has changed
                text_changed = old_text != new_text
                speaker_changed = old_speaker != new_speaker
                
                if text_changed or speaker_changed:
                    dialogue_changed = True
                    # Content changed - remove old audio file if it exists
                    if old_audio and old_audio.strip() and os.path.exists(old_audio):
                        try:
                            os.remove(old_audio)
                            deleted_audio_files.append(old_audio)
                            logger.info(f"🗑️ Deleted audio file for changed line {i}: {old_audio}")
                        except Exception as e:
                            logger.warning(f"⚠️ Could not delete audio file {old_audio}: {str(e)}")
                    
                    logger.info(f"📝 Line {i} changed - {'text' if text_changed else ''}{'speaker' if speaker_changed else ''} - audio cleared")
                else:
                    # Content unchanged - keep existing audio
                    if old_audio and old_audio.strip() and os.path.exists(old_audio):
                        new_dialogue_line["audioFile"] = old_audio
                        logger.info(f"✅ Line {i} unchanged - keeping existing audio: {old_audio}")
                    else:
                        logger.info(f"📝 Line {i} unchanged - no existing audio")
            else:
                # This is a new line
                dialogue_changed = True
                logger.info(f"➕ New line {i} added: {new_line.speaker} - {new_line.text[:30]}...")
            
            updated_dialogue.append(new_dialogue_line)
        
        # Handle case where new dialogue has fewer lines than old dialogue
        if len(old_dialogue) > len(new_dialogue_updates):
            dialogue_changed = True
            # Delete audio files for removed lines
            for i in range(len(new_dialogue_updates), len(old_dialogue)):
                old_line = old_dialogue[i]
                old_audio = old_line.get("audioFile", "")
                if old_audio and old_audio.strip() and os.path.exists(old_audio):
                    try:
                        os.remove(old_audio)
                        deleted_audio_files.append(old_audio)
                        logger.info(f"🗑️ Deleted audio file for removed line {i}: {old_audio}")
                    except Exception as e:
                        logger.warning(f"⚠️ Could not delete audio file {old_audio}: {str(e)}")
        
        # Update the script with new dialogue
        script_data["dialogue"] = updated_dialogue
        script_data["updatedAt"] = datetime.now().isoformat()
        
        # Clear video data if any dialogue was changed (since video will be outdated)
        if dialogue_changed:
            logger.info("🎬 Clearing video data since dialogue was modified")
            script_data["finalVideoPath"] = None
            script_data["videoDuration"] = None
        
        # Save updated scripts
        save_scripts(scripts_data)
        
        # Log summary
        audio_count = sum(1 for line in updated_dialogue if line.get("audioFile", "").strip() and os.path.exists(line.get("audioFile", "")))
        logger.info(f"📊 Script {script_id} update summary:")
        logger.info(f"   Total lines: {len(updated_dialogue)}")
        logger.info(f"   Lines with audio: {audio_count}")
        logger.info(f"   Audio files deleted: {len(deleted_audio_files)}")
        
        logger.info(f"✅ Updated script: {script_id}")
        
        return ScriptResponse(
            id=script_data["id"],
            selectedCharacters=script_data["selectedCharacters"],
            originalPrompt=script_data["originalPrompt"],
            word=script_data.get("word"),
            dialogue=updated_dialogue,
            createdAt=script_data["createdAt"],
            updatedAt=script_data["updatedAt"],
            hasAudio=audio_count > 0,
            audioCount=audio_count,
            finalVideoPath=script_data.get("finalVideoPath"),
            videoDuration=script_data.get("videoDuration")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating script {script_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/scripts/{script_id}")
async def delete_script(script_id: str):
    """Delete a script"""
    try:
        scripts_data = load_scripts()
        scripts = scripts_data.get("scripts", {})
        
        if script_id not in scripts:
            raise HTTPException(status_code=404, detail=f"Script '{script_id}' not found")
        
        # Delete associated audio files
        script = scripts[script_id]
        dialogue_lines = script.get("dialogue", [])
        deleted_audio_files = []
        
        for dialogue_line in dialogue_lines:
            audio_path = dialogue_line.get("audioFile", "")
            if audio_path and os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                    deleted_audio_files.append(audio_path)
                    logger.info(f"Deleted audio file: {audio_path}")
                except Exception as e:
                    logger.warning(f"Could not delete audio file {audio_path}: {str(e)}")
        
        # Delete the script
        del scripts[script_id]
        save_scripts(scripts_data)
        
        logger.info(f"Deleted script: {script_id}")
        
        return {
            "message": f"Script '{script_id}' deleted successfully",
            "deletedAudioFiles": deleted_audio_files
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting script {script_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Audio Generation Endpoints

@app.post("/api/scripts/{script_id}/generate-audio", response_model=AudioGenerationResponse)
async def generate_script_audio(script_id: str):
    """Generate audio files for a script"""
    logger.info(f"Audio generation requested for script: {script_id}")
    return await generate_audio_for_script(script_id)

@app.get("/api/scripts/{script_id}/audio-status")
async def get_audio_generation_status(script_id: str):
    """Get audio generation status for a script"""
    try:
        scripts_data = load_scripts()
        scripts = scripts_data.get("scripts", {})
        
        if script_id not in scripts:
            raise HTTPException(status_code=404, detail=f"Script '{script_id}' not found")
        
        script = scripts[script_id]
        dialogue_lines = script.get("dialogue", [])
        
        total_lines = len(dialogue_lines)
        completed_lines = 0
        
        # Count lines with valid audio files
        for dialogue_line in dialogue_lines:
            audio_file = dialogue_line.get("audioFile", "")
            if audio_file and os.path.exists(audio_file):
                completed_lines += 1
        
        if completed_lines == total_lines:
            status = "completed"
        elif completed_lines > 0:
            status = "partial"
        else:
            status = "pending"
        
        return AudioGenerationStatus(
            scriptId=script_id,
            status=status,
            totalLines=total_lines,
            processedLines=total_lines,
            completedLines=completed_lines,
            failedLines=total_lines - completed_lines
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audio status for script {script_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/f5tts/status")
async def get_f5tts_status():
    """Check F5-TTS service status"""
    try:
        is_connected = check_f5tts_connection()
        return {
            "status": "connected" if is_connected else "disconnected",
            "url": F5TTS_URL,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error checking F5-TTS status: {str(e)}")
        return {
            "status": "error",
            "url": F5TTS_URL,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Video Generation Endpoints

@app.post("/api/scripts/{script_id}/generate-video", response_model=VideoGenerationResponse)
async def generate_script_video(script_id: str, background_video: Optional[str] = None):
    """Generate video for a script with audio"""
    try:
        logger.info(f"🎬 Video generation requested for script: {script_id}")
        
        # Check if script exists
        scripts_data = load_scripts()
        scripts = scripts_data.get("scripts", {})
        
        if script_id not in scripts:
            raise HTTPException(status_code=404, detail=f"Script '{script_id}' not found")
        
        # Validate that all dialogue lines have audio files
        script = scripts[script_id]
        dialogue_lines = script.get("dialogue", [])
        
        if not dialogue_lines:
            raise HTTPException(status_code=400, detail="Script has no dialogue lines")
        
        missing_audio = []
        for i, line in enumerate(dialogue_lines):
            audio_file = line.get("audioFile", "")
            if not audio_file or not os.path.exists(audio_file):
                missing_audio.append(f"Line {i+1} ({line.get('speaker', 'unknown')})")
        
        if missing_audio:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot generate video: Missing audio files for {len(missing_audio)} lines. Generate all audio files first. Missing: {', '.join(missing_audio[:3])}{'...' if len(missing_audio) > 3 else ''}"
            )
        
        logger.info(f"✅ Audio validation passed: {len(dialogue_lines)} audio files ready")
        
        # Initialize video generator
        video_generator = VideoGenerator()
        
        # Generate video
        result = await video_generator.generate_video(script_id, background_video)
        
        logger.info(f"✅ Video generation completed for script: {script_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Video generation API error for script {script_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")

@app.get("/api/scripts/{script_id}/video-status", response_model=VideoGenerationStatus)
async def get_video_generation_status(script_id: str):
    """Get video generation status for a script"""
    try:
        scripts_data = load_scripts()
        scripts = scripts_data.get("scripts", {})
        
        if script_id not in scripts:
            raise HTTPException(status_code=404, detail=f"Script '{script_id}' not found")
        
        script = scripts[script_id]
        final_video_path = script.get("finalVideoPath", "")
        
        # Check if video exists and is valid
        if final_video_path and os.path.exists(final_video_path) and os.path.getsize(final_video_path) > 0:
            status = "completed"
            message = f"Video generated successfully: {os.path.basename(final_video_path)}"
            progress = 100.0
        else:
            # Check if all dialogue lines have audio (prerequisite for video generation)
            dialogue_lines = script.get("dialogue", [])
            total_lines = len(dialogue_lines)
            audio_lines = 0
            
            for line in dialogue_lines:
                audio_file = line.get("audioFile", "")
                if audio_file and os.path.exists(audio_file):
                    audio_lines += 1
            
            if audio_lines == total_lines and total_lines > 0:
                status = "pending"
                message = f"Ready for video generation ({audio_lines}/{total_lines} audio files ready)"
                progress = 0.0
            else:
                status = "pending"
                message = f"Waiting for audio generation ({audio_lines}/{total_lines} audio files ready)"
                progress = 0.0
        
        return VideoGenerationStatus(
            scriptId=script_id,
            status=status,
            stage="ready" if status == "pending" else "completed",
            progress=progress,
            message=message,
            finalVideoPath=final_video_path if final_video_path else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting video status for script {script_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/ffmpeg-status")
async def check_ffmpeg_status():
    """Check if FFmpeg is available"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return {
                "status": "available",
                "message": "FFmpeg is available and working",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "error",
                "message": "FFmpeg check failed",
                "timestamp": datetime.now().isoformat()
            }
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "message": "FFmpeg check timed out",
            "timestamp": datetime.now().isoformat()
        }
    except FileNotFoundError:
        return {
            "status": "not_found",
            "message": "FFmpeg not found in PATH",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"FFmpeg check error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    print("🚀 Starting Character Management API...")
    print(f"📁 API Data Directory: {os.path.abspath(API_DATA_DIR)}")
    print(f"🎵 Audio Files Directory: {os.path.abspath(AUDIO_FILES_DIR)}")
    print(f"🖼️  Images Directory: {os.path.abspath(IMAGES_DIR)}")
    print(f"📋 User Profiles File: {os.path.abspath(USER_PROFILES_FILE)}")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 