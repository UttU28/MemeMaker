#!/usr/bin/env python3

import json
import os
import shutil
import time
import requests
import subprocess
import random
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import logging
from openai import OpenAI
from dotenv import load_dotenv
from gradio_client import Client, handle_file
from pydub import AudioSegment
import warnings
import re
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn

# Import Pydantic Models
from models import (
    CharacterConfig, CharacterUpdate, CharacterResponse, SystemStatus,
    ScriptRequest, DialogueLine, ScriptResponse, ScriptUpdate,
    AudioGenerationStatus, AudioGenerationResponse,
    VideoGenerationStatus, VideoGenerationResponse,
    VideoGenerationJob, VideoGenerationJobResponse,
    SignupRequest, LoginRequest, UserResponse, AuthResponse,
    StarResponse, UserActivity, UserActivityResponse, ActivityStats
)

# Import Services
from utils import (
    loadUserProfiles, saveUserProfiles, generateCharacterId, getDefaultConfig,
    validateAudioFile, validateImageFile, loadScripts, saveScripts, generateScriptId
)
from audio_service import (
    checkF5ttsConnection, generateAudioFilename, generateAudioForScript, F5TTSClient
)
from video_service import VideoGenerator
from openai_service import getOpenaiClient, generateScriptWithOpenai
from firebase_service import initializeFirebaseService, getFirebaseService
from jwt_service import getJwtService
from background_video_service import get_background_video_service, initialize_background_video_service

load_dotenv()

API_DATA_DIR = "apiData"
USER_PROFILES_FILE = os.path.join(API_DATA_DIR, "userProfiles.json")
SCRIPTS_FILE = os.path.join(API_DATA_DIR, "scripts.json")
AUDIO_FILES_DIR = os.path.join(API_DATA_DIR, "audio_files")
GENERATED_AUDIO_DIR = os.path.join(AUDIO_FILES_DIR, "generated")
IMAGES_DIR = os.path.join(API_DATA_DIR, "images")
BACKGROUND_DIR = os.path.join(API_DATA_DIR, "background")
F5TTS_URL = "http://localhost:7860"
F5TTS_TIMEOUT = 300
VIDEO_OUTPUT_DIR = os.path.join(API_DATA_DIR, "video_output")
DEFAULT_BACKGROUND_VIDEO = "downloads/Minecraft Parkour Gameplay No Copyright_mobile.mp4"
FONT_PATH = 'C:/Windows/Fonts/impact.ttf'

os.makedirs(AUDIO_FILES_DIR, exist_ok=True)
os.makedirs(GENERATED_AUDIO_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(BACKGROUND_DIR, exist_ok=True)
os.makedirs(VIDEO_OUTPUT_DIR, exist_ok=True)

warnings.filterwarnings("ignore", category=UserWarning)

# Initialize Firebase Service
try:
    firebase_service = initializeFirebaseService("firebase.json")
    print("🔥 Firebase initialized successfully!")
except Exception as e:
    print(f"❌ Firebase initialization failed: {str(e)}")
    raise

# Initialize Background Video Service
try:
    initialize_background_video_service()
    print("🎬 Background video service initialized successfully!")
except Exception as e:
    print(f"❌ Background video service initialization failed: {str(e)}")

openai_key = os.getenv('OPENAI_API_KEY')
if openai_key:
    print(f"🔑 OpenAI API Key: {openai_key[:10]}...{openai_key[-4:]}")
else:
    print("❌ OpenAI API Key not found")

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Voice Cloning Character Management API",
    description="API for managing characters, audio files, and images for video generation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=".*",
)

# Mount static files for serving images
app.mount("/api/static", StaticFiles(directory=API_DATA_DIR), name="static")
# Mount video files for direct access
app.mount("/api/videos", StaticFiles(directory=VIDEO_OUTPUT_DIR), name="videos")

# JWT Authentication
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """JWT authentication dependency"""
    try:
        token = credentials.credentials
        jwt_service = getJwtService()
        
        payload = jwt_service.verifyToken(token)
        if not payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user data from Firebase
        firebase_service = getFirebaseService()
        user_data = firebase_service.getUserById(payload['user_id'])
        
        if not user_data:
            raise HTTPException(
                status_code=401,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 JWT authentication error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Add validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"💥 Validation error on {request.method} {request.url}")
    logger.error(f"💥 Validation details: {exc.errors()}")
    
    # Convert errors to JSON-serializable format
    serializable_errors = []
    for error in exc.errors():
        serializable_error = {
            "type": error.get("type"),
            "loc": error.get("loc"),
            "msg": error.get("msg"),
            "url": error.get("url")
        }
        # Convert input to string if it's not serializable
        if "input" in error:
            try:
                serializable_error["input"] = str(error["input"])
            except:
                serializable_error["input"] = "Non-serializable input"
        serializable_errors.append(serializable_error)
    
    return JSONResponse(
        status_code=422,
        content={"detail": serializable_errors}
    )

# Helper functions for converting file paths to URLs and datetime objects
def convert_datetime_to_string(dt_obj):
    """Convert Firebase datetime object to ISO string"""
    if hasattr(dt_obj, 'isoformat'):
        return dt_obj.isoformat()
    elif hasattr(dt_obj, 'timestamp'):
        return datetime.fromtimestamp(dt_obj.timestamp()).isoformat()
    else:
        return str(dt_obj)

def convert_local_path_to_url(local_path: str, request: Request = None) -> str:
    """Convert local file path to HTTP URL accessible by frontend"""
    if not local_path:
        return ""
    
    # Convert Windows backslashes to forward slashes
    clean_path = local_path.replace("\\", "/")
    
    # Remove the apiData prefix if present
    if clean_path.startswith("apiData/"):
        relative_path = clean_path[8:]  # Remove "apiData/"
    elif API_DATA_DIR in clean_path:
        # Handle full paths containing API_DATA_DIR
        relative_path = clean_path.split(API_DATA_DIR)[-1].lstrip("/\\")
    else:
        # Already relative path
        relative_path = clean_path
    
    # Return URL accessible through static files mount
    url = f"/api/static/{relative_path}"
    logger.debug(f"🔗 Converted path: '{local_path}' -> '{url}'")
    return url

def convert_images_dict_to_urls(images_dict: Dict[str, str], request: Request = None) -> Dict[str, str]:
    """Convert dictionary of image paths to URLs"""
    urls_dict = {
        key: convert_local_path_to_url(path, request) 
        for key, path in images_dict.items()
    }
    logger.debug(f"🖼️ Converted {len(images_dict)} image paths to URLs")
    return urls_dict

def build_character_response(char_id: str, char_data: Dict[str, Any], request: Request, current_user: Dict[str, Any]) -> CharacterResponse:
    """Build a complete CharacterResponse with ownership information"""
    try:
        # Basic character data
        audio_file = char_data.get("audioFile", "")
        has_audio = bool(audio_file and os.path.exists(audio_file))
        
        # Convert file paths to URLs
        audio_url = convert_local_path_to_url(audio_file, request)
        images = char_data.get("images", {})
        images_urls = convert_images_dict_to_urls(images, request)
        image_count = len(images)
        
        # Configuration
        config_data = char_data.get("config", {})
        default_config = getDefaultConfig(USER_PROFILES_FILE)
        
        config = CharacterConfig(
            speed=config_data.get("speed", default_config.speed),
            nfeSteps=config_data.get("nfeSteps", default_config.nfeSteps),
            crossFadeDuration=config_data.get("crossFadeDuration", default_config.crossFadeDuration),
            removeSilences=config_data.get("removeSilences", default_config.removeSilences)
        )
        
        # Ownership information
        created_by = char_data.get("createdBy")
        created_by_name = None
        is_owner = False
        
        if created_by:
            # Get creator's name
            firebase_service = getFirebaseService()
            created_by_name = firebase_service.getUserNameById(created_by)
            
            # Check if current user is the owner
            is_owner = (current_user and current_user.get('id') == created_by)
        
        # Star information
        starred_count = char_data.get("starred", 0)
        is_starred = False
        if current_user:
            firebase_service = getFirebaseService()
            is_starred = firebase_service.isCharacterStarredByUser(char_id, current_user.get('id'))
        
        return CharacterResponse(
            id=char_id,
            displayName=char_data.get("displayName", char_id.title()),
            audioFile=audio_url,
            config=config,
            images=images_urls,
            outputPrefix=char_data.get("outputPrefix", char_id),
            createdAt=char_data.get("createdAt", datetime.now().isoformat()),
            updatedAt=char_data.get("updatedAt", datetime.now().isoformat()),
            hasAudio=has_audio,
            imageCount=image_count,
            createdBy=created_by,
            createdByName=created_by_name,
            isOwner=is_owner,
            starred=starred_count,
            isStarred=is_starred
        )
        
    except Exception as e:
        logger.error(f"💥 Error building character response: {str(e)}")
        raise

# API Endpoints

@app.get("/")
async def root():
    return {"message": "Hello Duniya"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Authentication Endpoints

@app.post("/api/signup", response_model=AuthResponse)
async def signup(request: SignupRequest):
    try:
        logger.info(f"🔐 Signup request for email: {request.email}")
        
        # Get Firebase service
        firebase_service = getFirebaseService()
        
        # Create user in Firebase Auth and Firestore
        success, message, user_id = firebase_service.createUser(
            request.email, 
            request.password, 
            request.name
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        # Get user data from Firestore
        user_data = firebase_service.getUserById(user_id)
        if not user_data:
            raise HTTPException(status_code=500, detail="Failed to retrieve user data after creation")
        
        # Create JWT token
        jwt_service = getJwtService()
        token, expires_in = jwt_service.createToken(user_id, request.email)
        
        # Create user response
        user_response = UserResponse(
            id=user_data['id'],
            name=user_data['name'],
            email=user_data['email'],
            isVerified=user_data['isVerified'],
            subscription=user_data['subscription'],
            createdAt=convert_datetime_to_string(user_data['createdAt']),
            updatedAt=convert_datetime_to_string(user_data['updatedAt'])
        )
        
        logger.info(f"✅ User signup successful: {request.email}")
        
        return AuthResponse(
            success=True,
            message="User created successfully",
            token=token,
            user=user_response,
            expiresIn=expires_in
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Signup error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")

@app.post("/api/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    try:
        logger.info(f"🔐 Login request for email: {request.email}")
        
        # Get Firebase service
        firebase_service = getFirebaseService()
        
        # Verify user credentials (email and password)
        success, message, user_id = firebase_service.verifyUserPassword(request.email, request.password)
        if not success:
            logger.warning(f"🔒 Login failed for {request.email}: {message}")
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Get user data from Firestore
        user_data = firebase_service.getUserById(user_id)
        if not user_data:
            raise HTTPException(status_code=500, detail="Failed to retrieve user data")
        
        # Create JWT token
        jwt_service = getJwtService()
        token, expires_in = jwt_service.createToken(user_id, request.email)
        
        # Create user response
        user_response = UserResponse(
            id=user_data['id'],
            name=user_data['name'],
            email=user_data['email'],
            isVerified=user_data['isVerified'],
            subscription=user_data['subscription'],
            createdAt=convert_datetime_to_string(user_data['createdAt']),
            updatedAt=convert_datetime_to_string(user_data['updatedAt'])
        )
        
        logger.info(f"✅ User login successful: {request.email}")
        
        return AuthResponse(
            success=True,
            message="Login successful",
            token=token,
            user=user_response,
            expiresIn=expires_in
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.get("/api/me", response_model=UserResponse)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile (requires authentication)"""
    try:
        return UserResponse(
            id=current_user['id'],
            name=current_user['name'],
            email=current_user['email'],
            isVerified=current_user['isVerified'],
            subscription=current_user['subscription'],
            createdAt=convert_datetime_to_string(current_user['createdAt']),
            updatedAt=convert_datetime_to_string(current_user['updatedAt'])
        )
    except Exception as e:
        logger.error(f"💥 Error getting user profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user profile")

@app.post("/api/refresh-token", response_model=AuthResponse)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Refresh JWT token"""
    try:
        old_token = credentials.credentials
        jwt_service = getJwtService()
        
        result = jwt_service.refreshToken(old_token)
        if not result:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        new_token, expires_in = result
        
        # Get user data from the old token
        payload = jwt_service.decodeTokenWithoutVerification(old_token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token format")
        
        firebase_service = getFirebaseService()
        user_data = firebase_service.getUserById(payload['user_id'])
        
        if not user_data:
            raise HTTPException(status_code=401, detail="User not found")
        
        user_response = UserResponse(
            id=user_data['id'],
            name=user_data['name'],
            email=user_data['email'],
            isVerified=user_data['isVerified'],
            subscription=user_data['subscription'],
            createdAt=convert_datetime_to_string(user_data['createdAt']),
            updatedAt=convert_datetime_to_string(user_data['updatedAt'])
        )
        
        return AuthResponse(
            success=True,
            message="Token refreshed successfully",
            token=new_token,
            user=user_response,
            expiresIn=expires_in
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Token refresh error: {str(e)}")
        raise HTTPException(status_code=500, detail="Token refresh failed")

@app.get("/api/system/status", response_model=SystemStatus)
async def get_system_status():
    try:
        profiles = loadUserProfiles(USER_PROFILES_FILE)
        total_characters = len(profiles.get("users", {}))
        
        return SystemStatus(
            status="active",
            totalCharacters=total_characters,
            timestamp=datetime.now().isoformat(),
            apiDataDir=os.path.abspath(API_DATA_DIR)
        )
    except Exception as e:
        logger.error(f"💥 Error getting system status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/characters", response_model=List[CharacterResponse])
async def list_characters(request: Request, current_user: dict = Depends(get_current_user)):
    try:
        profiles = loadUserProfiles(USER_PROFILES_FILE)
        users = profiles.get("users", {})
        
        characters = []
        for char_id, char_data in users.items():
            character = build_character_response(char_id, char_data, request, current_user)
            characters.append(character)
        
        return characters
    except Exception as e:
        logger.error(f"💥 Error listing characters: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/characters/{character_id}", response_model=CharacterResponse)
async def get_character(character_id: str, request: Request, current_user: dict = Depends(get_current_user)):
    try:
        profiles = loadUserProfiles(USER_PROFILES_FILE)
        users = profiles.get("users", {})
        
        if character_id not in users:
            raise HTTPException(status_code=404, detail=f"Character '{character_id}' not found")
        
        char_data = users[character_id]
        
        return build_character_response(character_id, char_data, request, current_user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error getting character {character_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/characters/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
    displayName: Optional[str] = Form(None),
    speed: Optional[str] = Form(None),
    nfeSteps: Optional[str] = Form(None),
    crossFadeDuration: Optional[str] = Form(None),
    removeSilences: Optional[str] = Form(None),
    removeImageKeys: Optional[str] = Form(None),
    newImageFiles: List[UploadFile] = File(default=[])
):
    try:
        logger.info(f"🔄 Updating character: {character_id}")
        logger.info(f"📝 Received data - displayName: {displayName}, speed: {speed}, nfeSteps: {nfeSteps}")
        logger.info(f"📝 crossFadeDuration: {crossFadeDuration}, removeSilences: {removeSilences}")
        logger.info(f"🖼️ New images: {len(newImageFiles) if newImageFiles else 0}, Remove keys: {removeImageKeys}")
        
        # Check ownership first
        firebase_service = getFirebaseService()
        char_data = firebase_service.getUserProfile(character_id)
        
        if not char_data:
            raise HTTPException(status_code=404, detail=f"Character '{character_id}' not found")
        
        # Verify ownership
        character_owner = char_data.get('createdBy')
        if character_owner and character_owner != current_user['id']:
            raise HTTPException(
                status_code=403, 
                detail=f"Access denied. You can only modify characters you created."
            )
        current_time = datetime.now().isoformat()
        
        # Update basic info
        if displayName is not None and displayName.strip():
            char_data["displayName"] = displayName.strip()
        
        # Update config if provided
        if any(param is not None and param.strip() for param in [speed, nfeSteps, crossFadeDuration] if param) or removeSilences is not None:
            if "config" not in char_data:
                char_data["config"] = {}
            
            try:
                if speed is not None and speed.strip():
                    char_data["config"]["speed"] = float(speed)
                if nfeSteps is not None and nfeSteps.strip():
                    char_data["config"]["nfeSteps"] = int(nfeSteps)
                if crossFadeDuration is not None and crossFadeDuration.strip():
                    char_data["config"]["crossFadeDuration"] = float(crossFadeDuration)
                if removeSilences is not None:
                    # Handle boolean conversion from form data
                    char_data["config"]["removeSilences"] = removeSilences.lower() in ('true', '1', 'on', 'yes')
            except (ValueError, AttributeError) as e:
                logger.error(f"💥 Error parsing config values: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Invalid config values: {str(e)}")
        
        # Handle image removal
        if removeImageKeys:
            keys_to_remove = [key.strip() for key in removeImageKeys.split(',') if key.strip()]
            existing_images = char_data.get("images", {})
            
            for key in keys_to_remove:
                if key in existing_images:
                    image_path = existing_images[key]
                    if os.path.exists(image_path):
                        try:
                            os.remove(image_path)
                            logger.info(f"🗑️ Removed image: {image_path}")
                        except Exception as e:
                            logger.warning(f"⚠️ Could not delete image {image_path}: {str(e)}")
                    del existing_images[key]
                    logger.info(f"✅ Removed image key: {key}")
            
            char_data["images"] = existing_images
        
        # Handle new image uploads
        if newImageFiles and len(newImageFiles) > 0:
            valid_new_images = []
            for img in newImageFiles:
                # Skip empty file uploads (when no file is selected, FastAPI sends an empty UploadFile)
                if (img and hasattr(img, 'filename') and img.filename and 
                    img.filename.strip() and img.filename != '' and validateImageFile(img)):
                    valid_new_images.append(img)
                    logger.info(f"✅ Valid image file: {img.filename}")
                elif img and hasattr(img, 'filename') and img.filename:
                    logger.warning(f"⚠️ Skipping invalid image: {img.filename}")
                else:
                    logger.info(f"⚠️ Skipping empty file upload slot")
            
            if valid_new_images:
                existing_images = char_data.get("images", {})
                
                # Check total image count limit
                if len(existing_images) + len(valid_new_images) > 10:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Cannot add {len(valid_new_images)} images. Character already has {len(existing_images)} images. Maximum 10 images allowed."
                    )
                
                # Find the next available index
                existing_indices = set()
                for key in existing_images.keys():
                    try:
                        existing_indices.add(int(key))
                    except ValueError:
                        pass
                
                next_index = 0
                while next_index in existing_indices:
                    next_index += 1
                
                # Add new images
                for img in valid_new_images:
                    try:
                        image_extension = Path(img.filename).suffix.lower()
                        image_filename = f"{character_id}_{next_index}{image_extension}"
                        image_path = os.path.join(IMAGES_DIR, image_filename)
                        
                        with open(image_path, "wb") as buffer:
                            shutil.copyfileobj(img.file, buffer)
                        
                        existing_images[str(next_index)] = image_path
                        logger.info(f"✅ Added new image: {image_filename}")
                        next_index += 1
                        
                    except Exception as e:
                        logger.error(f"💥 Error saving new image: {str(e)}")
                        continue
                
                char_data["images"] = existing_images
        
        # Prepare update data (only fields that were provided)
        update_data = {}
        if displayName is not None and displayName.strip():
            update_data["displayName"] = displayName.strip()
        
        # Add config updates
        if any(param is not None and param.strip() for param in [speed, nfeSteps, crossFadeDuration] if param) or removeSilences is not None:
            config_updates = {}
            try:
                if speed is not None and speed.strip():
                    config_updates["speed"] = float(speed)
                if nfeSteps is not None and nfeSteps.strip():
                    config_updates["nfeSteps"] = int(nfeSteps)
                if crossFadeDuration is not None and crossFadeDuration.strip():
                    config_updates["crossFadeDuration"] = float(crossFadeDuration)
                if removeSilences is not None:
                    config_updates["removeSilences"] = removeSilences.lower() in ('true', '1', 'on', 'yes')
                
                if config_updates:
                    # Merge with existing config
                    existing_config = char_data.get("config", {})
                    existing_config.update(config_updates)
                    update_data["config"] = existing_config
                    
            except (ValueError, AttributeError) as e:
                logger.error(f"💥 Error parsing config values: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Invalid config values: {str(e)}")
        
        # Add image updates
        if char_data.get("images") is not None:
            update_data["images"] = char_data["images"]
        
        # Use Firebase update with ownership check
        success = firebase_service.updateCharacterWithOwnerCheck(
            character_id, 
            update_data, 
            current_user['id']
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update character")
        
        # Log character update activity
        firebase_service.addCharacterActivity(
            current_user['id'], 
            firebase_service.ActivityType.CHARACTER_UPDATED, 
            character_id, 
            char_data.get("displayName", character_id)
        )
        
        logger.info(f"✅ Updated character: {character_id}")
        
        return await get_character(character_id, request, current_user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error updating character {character_id}: {str(e)}")
        logger.error(f"💥 Exception type: {type(e)}")
        logger.error(f"💥 Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/characters/{character_id}")
async def delete_character(character_id: str, current_user: dict = Depends(get_current_user)):
    try:
        # Get character data before deletion and check ownership
        firebase_service = getFirebaseService()
        char_data = firebase_service.getUserProfile(character_id)
        
        if not char_data:
            raise HTTPException(status_code=404, detail=f"Character '{character_id}' not found")
        
        # Verify ownership
        character_owner = char_data.get('createdBy')
        if character_owner and character_owner != current_user['id']:
            raise HTTPException(
                status_code=403, 
                detail=f"Access denied. You can only delete characters you created."
            )
        
        deleted_files = []
        
        # Delete audio file
        audio_file = char_data.get("audioFile", "")
        if audio_file and os.path.exists(audio_file):
            try:
                os.remove(audio_file)
                deleted_files.append(audio_file)
                logger.info(f"🗑️ Deleted audio: {audio_file}")
            except Exception as e:
                logger.warning(f"⚠️ Could not delete audio {audio_file}: {str(e)}")
        
        # Delete image files
        images = char_data.get("images", {})
        for image_path in images.values():
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    deleted_files.append(image_path)
                    logger.info(f"🗑️ Deleted image: {image_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not delete image {image_path}: {str(e)}")
        
        # Delete from Firebase with owner cleanup
        success = firebase_service.deleteCharacterWithOwnerCleanup(character_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete character from database")
        
        # Log character deletion activity
        firebase_service.addCharacterActivity(
            current_user['id'], 
            firebase_service.ActivityType.CHARACTER_DELETED, 
            character_id, 
            char_data.get("displayName", character_id)
        )
        
        # Handle default user update if needed
        profiles = firebase_service.getAllUserProfiles()
        if profiles.get("defaultUser") == character_id:
            remaining_users = list(profiles.get("users", {}).keys())
            new_default = remaining_users[0] if remaining_users else None
            
            # Update metadata with new default user
            if new_default != profiles.get("defaultUser"):
                # We need to update the metadata document
                try:
                    from datetime import datetime
                    firebase_service.db.collection('user_profiles').document('_metadata').set({
                        'defaultUser': new_default,
                        'updatedAt': datetime.now()
                    })
                    logger.info(f"🔄 Updated default user to: {new_default}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not update default user: {str(e)}")
        
        logger.info(f"✅ Deleted character: {character_id}")
        
        return {
            "message": f"Character '{character_id}' deleted successfully",
            "deletedFiles": deleted_files
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error deleting character {character_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/characters/complete", response_model=CharacterResponse)
async def create_complete_character(
    request: Request,
    current_user: dict = Depends(get_current_user),
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
        character_id = generateCharacterId(displayName, USER_PROFILES_FILE)
        
        if not validateAudioFile(audioFile):
            raise HTTPException(
                status_code=400, 
                detail="Invalid audio file. Supported formats: WAV, MP3, M4A, FLAC, OGG. Max size: 50MB"
            )
        
        if len(imageFiles) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 images allowed per character")
        
        valid_images = []
        for img in imageFiles:
            if validateImageFile(img):
                valid_images.append(img)
            else:
                logger.warning(f"⚠️ Skipping invalid image: {img.filename}")
        
        if not valid_images:
            raise HTTPException(status_code=400, detail="At least one valid image is required")
        
        default_config = getDefaultConfig(USER_PROFILES_FILE)
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
                logger.error(f"💥 Error saving image {index}: {str(e)}")
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
            # Use new ownership tracking method
            firebase_service = getFirebaseService()
            success = firebase_service.createCharacterWithOwner(
                character_id, 
                char_data, 
                current_user['id']
            )
            
            if not success:
                raise Exception("Failed to save character with ownership tracking")
            
            # Log character creation activity
            firebase_service.addCharacterActivity(
                current_user['id'], 
                firebase_service.ActivityType.CHARACTER_CREATED, 
                character_id, 
                displayName
            )
            
            logger.info(f"✅ Created character: {character_id} ({displayName}) for user {current_user['id']}")
            
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
        
        # Build response using helper function (char_data already has createdBy)
        return build_character_response(character_id, char_data, request, current_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error creating character: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/api/scripts/generate", response_model=ScriptResponse)
async def generateScript(request: ScriptRequest, currentUser: dict = Depends(get_current_user)):
    try:
        logger.info(f"🎬 User {currentUser['email']} generating script for characters: {request.selectedCharacters}")
        
        # Load user profiles to validate characters
        userProfiles = loadUserProfiles(USER_PROFILES_FILE)
        users = userProfiles.get("users", {})
        
        # Validate all selected characters exist
        for charId in request.selectedCharacters:
            if charId not in users:
                logger.warning(f"❌ Character '{charId}' not found for user {currentUser['email']}")
                raise HTTPException(status_code=400, detail=f"Character '{charId}' not found")
        
        # Generate dialogue using OpenAI
        logger.info(f"🤖 Generating dialogue with OpenAI for prompt: {request.prompt[:50]}...")
        dialogueLines = await generateScriptWithOpenai(
            request.selectedCharacters, 
            request.prompt
        )
        
        # Create unique script ID and timestamps
        scriptId = generateScriptId()
        currentTime = datetime.now().isoformat()
        
        # Build script data (ownership fields will be added by Firebase service)
        scriptData = {
            "id": scriptId,
            "selectedCharacters": request.selectedCharacters,
            "originalPrompt": request.prompt,
            "dialogue": [{"speaker": line.speaker, "text": line.text, "audioFile": ""} for line in dialogueLines],
            "createdByName": currentUser['name']  # Keep display name for convenience
        }
        
        # Save script to Firebase with associations
        firebaseService = getFirebaseService()
        success = firebaseService.createScriptWithAssociations(scriptId, scriptData, currentUser['id'])
        
        if not success:
            logger.error(f"💥 Failed to save script {scriptId} to Firebase")
            raise HTTPException(status_code=500, detail="Failed to save script to database")
        
        # Log script creation activity
        firebaseService.addScriptActivity(
            currentUser['id'], 
            firebaseService.ActivityType.SCRIPT_CREATED, 
            scriptId, 
            request.prompt[:50] + "..." if len(request.prompt) > 50 else request.prompt
        )
        
        logger.info(f"✅ Generated script {scriptId} for user {currentUser['email']} with {len(dialogueLines)} dialogue lines")
        
        return ScriptResponse(
            id=scriptData["id"],
            selectedCharacters=scriptData["selectedCharacters"],
            originalPrompt=scriptData["originalPrompt"],
            dialogue=scriptData["dialogue"],
            createdAt=scriptData["createdAt"],
            updatedAt=scriptData["updatedAt"],
            hasAudio=False,
            audioCount=0,
            finalVideoPath=None,
            videoDuration=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Script generation failed for user {currentUser['email']}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate script: {str(e)}")

@app.get("/api/scripts", response_model=List[ScriptResponse])
async def listScripts(currentUser: dict = Depends(get_current_user)):
    try:
        logger.info(f"📋 User {currentUser['email']} requesting all scripts")
        
        # Get all scripts from Firebase
        firebaseService = getFirebaseService()
        scriptsData = firebaseService.getAllScripts()
        scripts = scriptsData.get("scripts", {})
        
        scriptResponses = []
        userScriptCount = 0
        otherScriptCount = 0
        
        for scriptData in scripts.values():
            # Check if this script belongs to current user
            isOwner = scriptData.get("createdBy") == currentUser['id']
            if isOwner:
                userScriptCount += 1
                continue  # Skip user's own scripts - they can get them from /api/my-scripts
            
            dialogueLines = scriptData.get("dialogue", [])
            
            # Count audio files that exist
            audioCount = 0
            for dialogueLine in dialogueLines:
                audioFile = dialogueLine.get("audioFile", "")
                if audioFile and os.path.exists(audioFile):
                    audioCount += 1
            
            scriptResponse = ScriptResponse(
                id=scriptData["id"],
                selectedCharacters=scriptData["selectedCharacters"],
                originalPrompt=scriptData["originalPrompt"],
                dialogue=dialogueLines,
                createdAt=scriptData["createdAt"],
                updatedAt=scriptData["updatedAt"],
                hasAudio=audioCount > 0,
                audioCount=audioCount,
                finalVideoPath=scriptData.get("finalVideoPath"),
                videoDuration=scriptData.get("videoDuration"),
                videoSize=scriptData.get("videoSize")
            )
            scriptResponses.append(scriptResponse)
            otherScriptCount += 1
        
        logger.info(f"📊 Retrieved {otherScriptCount} other users' scripts (excluded {userScriptCount} owned by {currentUser['email']})")
        return scriptResponses
        
    except Exception as e:
        logger.error(f"💥 Failed to list scripts for user {currentUser['email']}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list scripts: {str(e)}")

@app.get("/api/scripts/{scriptId}", response_model=ScriptResponse)
async def getScript(scriptId: str, currentUser: dict = Depends(get_current_user)):
    try:
        logger.info(f"🔍 User {currentUser['email']} requesting script: {scriptId}")
        
        # Get script from Firebase
        firebaseService = getFirebaseService()
        scriptData = firebaseService.getScript(scriptId)
        
        if not scriptData:
            logger.warning(f"❌ Script '{scriptId}' not found for user {currentUser['email']}")
            raise HTTPException(status_code=404, detail=f"Script '{scriptId}' not found")
        
        dialogueLines = scriptData.get("dialogue", [])
        
        # Count existing audio files
        audioCount = 0
        for dialogueLine in dialogueLines:
            audioFile = dialogueLine.get("audioFile", "")
            if audioFile and os.path.exists(audioFile):
                audioCount += 1
        
        # Check ownership
        isOwner = scriptData.get("createdBy") == currentUser['id']
        ownerInfo = f" (Owner: {scriptData.get('createdByName', 'Unknown')})" if not isOwner else " (Your script)"
        
        logger.info(f"✅ Retrieved script {scriptId} for user {currentUser['email']}{ownerInfo}")
        
        return ScriptResponse(
            id=scriptData["id"],
            selectedCharacters=scriptData["selectedCharacters"],
            originalPrompt=scriptData["originalPrompt"],
            dialogue=dialogueLines,
            createdAt=scriptData["createdAt"],
            updatedAt=scriptData["updatedAt"],
            hasAudio=audioCount > 0,
            audioCount=audioCount,
            finalVideoPath=scriptData.get("finalVideoPath"),
            videoDuration=scriptData.get("videoDuration"),
            videoSize=scriptData.get("videoSize")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Failed to get script {scriptId} for user {currentUser['email']}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get script: {str(e)}")

@app.put("/api/scripts/{scriptId}", response_model=ScriptResponse)
async def updateScript(scriptId: str, updates: ScriptUpdate, currentUser: dict = Depends(get_current_user)):
    try:
        logger.info(f"✏️ User {currentUser['email']} updating script: {scriptId}")
        
        # Get script from Firebase
        firebaseService = getFirebaseService()
        scriptData = firebaseService.getScript(scriptId)
        
        if not scriptData:
            logger.warning(f"❌ Script '{scriptId}' not found for user {currentUser['email']}")
            raise HTTPException(status_code=404, detail=f"Script '{scriptId}' not found")
        
        # Check ownership (users can only edit their own scripts)
        scriptOwner = scriptData.get("createdBy")
        if scriptOwner and scriptOwner != currentUser['id']:
            logger.warning(f"🚫 User {currentUser['email']} denied access to edit script {scriptId} (owned by {scriptData.get('createdByName', 'Unknown')})")
            raise HTTPException(
                status_code=403, 
                detail="Access denied. You can only edit scripts you created."
            )
        
        oldDialogue = scriptData.get("dialogue", [])
        newDialogueUpdates = updates.dialogue
        
        logger.info(f"📝 Updating script {scriptId} with {len(newDialogueUpdates)} dialogue lines")
        
        updatedDialogue = []
        deletedAudioFiles = []
        dialogueChanged = False
        
        # Process each dialogue line for changes
        for i, newLine in enumerate(newDialogueUpdates):
            oldLine = oldDialogue[i] if i < len(oldDialogue) else None
            
            newDialogueLine = {
                "speaker": newLine.speaker,
                "text": newLine.text,
                "audioFile": ""
            }
            
            if oldLine:
                oldText = oldLine.get("text", "").strip()
                oldSpeaker = oldLine.get("speaker", "").strip()
                oldAudio = oldLine.get("audioFile", "")
                
                newText = newLine.text.strip()
                newSpeaker = newLine.speaker.strip()
                
                textChanged = oldText != newText
                speakerChanged = oldSpeaker != newSpeaker
                
                if textChanged or speakerChanged:
                    dialogueChanged = True
                    # Delete old audio file if text or speaker changed
                    if oldAudio and oldAudio.strip() and os.path.exists(oldAudio):
                        try:
                            os.remove(oldAudio)
                            deletedAudioFiles.append(oldAudio)
                            logger.info(f"🗑️ Deleted audio file for changed line {i}: {oldAudio}")
                        except Exception as e:
                            logger.warning(f"⚠️ Could not delete audio file {oldAudio}: {str(e)}")
                    
                    changeType = "text" if textChanged else ""
                    changeType += " speaker" if speakerChanged else ""
                    logger.info(f"📝 Line {i} changed ({changeType.strip()}) - audio cleared")
                else:
                    # Keep existing audio if line unchanged
                    if oldAudio and oldAudio.strip() and os.path.exists(oldAudio):
                        newDialogueLine["audioFile"] = oldAudio
                        logger.info(f"✅ Line {i} unchanged - keeping existing audio")
                    else:
                        logger.info(f"📝 Line {i} unchanged - no existing audio")
            else:
                dialogueChanged = True
                logger.info(f"➕ New line {i} added: {newLine.speaker} - {newLine.text[:30]}...")
            
            updatedDialogue.append(newDialogueLine)
        
        # Handle removed lines
        if len(oldDialogue) > len(newDialogueUpdates):
            dialogueChanged = True
            for i in range(len(newDialogueUpdates), len(oldDialogue)):
                oldLine = oldDialogue[i]
                oldAudio = oldLine.get("audioFile", "")
                if oldAudio and oldAudio.strip() and os.path.exists(oldAudio):
                    try:
                        os.remove(oldAudio)
                        deletedAudioFiles.append(oldAudio)
                        logger.info(f"🗑️ Deleted audio file for removed line {i}: {oldAudio}")
                    except Exception as e:
                        logger.warning(f"⚠️ Could not delete audio file {oldAudio}: {str(e)}")
        
        # Update script data
        scriptData["dialogue"] = updatedDialogue
        scriptData["updatedAt"] = datetime.now().isoformat()
        
        # Clear video data if dialogue changed
        if dialogueChanged:
            logger.info("🎬 Clearing video data since dialogue was modified")
            scriptData["finalVideoPath"] = None
            scriptData["videoDuration"] = None
            scriptData["videoSize"] = None
        
        # Save to Firebase
        success = firebaseService.saveScript(scriptId, scriptData)
        if not success:
            logger.error(f"💥 Failed to save updated script {scriptId} to Firebase")
            raise HTTPException(status_code=500, detail="Failed to save script updates")
        
        # Log script update activity
        firebaseService.addScriptActivity(
            currentUser['id'], 
            firebaseService.ActivityType.SCRIPT_UPDATED, 
            scriptId, 
            scriptData.get("originalPrompt", "")[:50] + "..." if len(scriptData.get("originalPrompt", "")) > 50 else scriptData.get("originalPrompt", scriptId)
        )
        
        # Count remaining audio files
        audioCount = sum(1 for line in updatedDialogue if line.get("audioFile", "").strip() and os.path.exists(line.get("audioFile", "")))
        
        logger.info(f"📊 Script {scriptId} update summary for user {currentUser['email']}:")
        logger.info(f"   • Total lines: {len(updatedDialogue)}")
        logger.info(f"   • Lines with audio: {audioCount}")
        logger.info(f"   • Audio files deleted: {len(deletedAudioFiles)}")
        logger.info(f"   • Dialogue changed: {'Yes' if dialogueChanged else 'No'}")
        
        logger.info(f"✅ Successfully updated script {scriptId}")
        
        return ScriptResponse(
            id=scriptData["id"],
            selectedCharacters=scriptData["selectedCharacters"],
            originalPrompt=scriptData["originalPrompt"],
            dialogue=updatedDialogue,
            createdAt=scriptData["createdAt"],
            updatedAt=scriptData["updatedAt"],
            hasAudio=audioCount > 0,
            audioCount=audioCount,
            finalVideoPath=scriptData.get("finalVideoPath"),
            videoDuration=scriptData.get("videoDuration"),
            videoSize=scriptData.get("videoSize")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Failed to update script {scriptId} for user {currentUser['email']}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update script: {str(e)}")

@app.delete("/api/scripts/{scriptId}")
async def deleteScript(scriptId: str, currentUser: dict = Depends(get_current_user)):
    try:
        logger.info(f"🗑️ User {currentUser['email']} attempting to delete script: {scriptId}")
        
        # Get script data before deletion
        firebaseService = getFirebaseService()
        script = firebaseService.getScript(scriptId)
        
        if not script:
            logger.warning(f"❌ Script '{scriptId}' not found for user {currentUser['email']}")
            raise HTTPException(status_code=404, detail=f"Script '{scriptId}' not found")
        
        # Check ownership (users can only delete their own scripts)
        scriptOwner = script.get("createdBy")
        if scriptOwner and scriptOwner != currentUser['id']:
            logger.warning(f"🚫 User {currentUser['email']} denied access to delete script {scriptId} (owned by {script.get('createdByName', 'Unknown')})")
            raise HTTPException(
                status_code=403, 
                detail="Access denied. You can only delete scripts you created."
            )
        
        dialogueLines = script.get("dialogue", [])
        deletedMediaFiles = []
        
        # Delete audio files
        for dialogueLine in dialogueLines:
            audioPath = dialogueLine.get("audioFile", "")
            if audioPath and os.path.exists(audioPath):
                try:
                    os.remove(audioPath)
                    deletedMediaFiles.append(audioPath)
                    logger.info(f"🗑️ Deleted audio: {os.path.basename(audioPath)}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not delete audio {audioPath}: {str(e)}")
        
        # Delete video file if exists
        finalVideoPath = script.get("finalVideoPath", "")
        if finalVideoPath and os.path.exists(finalVideoPath):
            try:
                os.remove(finalVideoPath)
                deletedMediaFiles.append(finalVideoPath)
                logger.info(f"🗑️ Deleted video: {os.path.basename(finalVideoPath)}")
            except Exception as e:
                logger.warning(f"⚠️ Could not delete video {finalVideoPath}: {str(e)}")
        
        # Delete from Firebase with associations cleanup
        success = firebaseService.deleteScriptWithAssociations(scriptId)
        if not success:
            logger.error(f"💥 Failed to delete script {scriptId} from Firebase")
            raise HTTPException(status_code=500, detail="Failed to delete script from database")
        
        # Log script deletion activity
        firebaseService.addScriptActivity(
            currentUser['id'], 
            firebaseService.ActivityType.SCRIPT_DELETED, 
            scriptId, 
            script.get("originalPrompt", "")[:50] + "..." if len(script.get("originalPrompt", "")) > 50 else script.get("originalPrompt", scriptId)
        )
        
        logger.info(f"✅ Successfully deleted script {scriptId} for user {currentUser['email']} ({len(deletedMediaFiles)} media files removed)")
        
        return {
            "message": f"Script '{scriptId}' deleted successfully",
            "deletedMediaFiles": deletedMediaFiles,
            "deletedCount": len(deletedMediaFiles)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Failed to delete script {scriptId} for user {currentUser['email']}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete script: {str(e)}")

@app.get("/api/scripts/{scriptId}/audio-status")
async def getAudioGenerationStatus(scriptId: str, currentUser: dict = Depends(get_current_user)):
    try:
        logger.info(f"🎵 User {currentUser['email']} checking audio status for script: {scriptId}")
        
        # Get script from Firebase
        firebaseService = getFirebaseService()
        script = firebaseService.getScript(scriptId)
        
        if not script:
            logger.warning(f"❌ Script '{scriptId}' not found for user {currentUser['email']}")
            raise HTTPException(status_code=404, detail=f"Script '{scriptId}' not found")
        
        dialogueLines = script.get("dialogue", [])
        totalLines = len(dialogueLines)
        completedLines = 0
        
        # Count completed audio files
        for dialogueLine in dialogueLines:
            audioFile = dialogueLine.get("audioFile", "")
            if audioFile and os.path.exists(audioFile):
                completedLines += 1
        
        # Determine status
        if completedLines == totalLines and totalLines > 0:
            status = "completed"
        elif completedLines > 0:
            status = "partial"
        else:
            status = "pending"
        
        # Check ownership for logging
        isOwner = script.get("createdBy") == currentUser['id']
        ownerInfo = " (Your script)" if isOwner else f" (Owner: {script.get('createdByName', 'Unknown')})"
        
        logger.info(f"📊 Audio status for script {scriptId}{ownerInfo}: {completedLines}/{totalLines} completed ({status})")
        
        return AudioGenerationStatus(
            scriptId=scriptId,
            status=status,
            totalLines=totalLines,
            processedLines=totalLines,
            completedLines=completedLines,
            failedLines=totalLines - completedLines
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Failed to get audio status for script {scriptId} for user {currentUser['email']}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get audio status: {str(e)}")

@app.post("/api/scripts/{scriptId}/generate-audio", response_model=AudioGenerationResponse)
async def generateScriptAudio(scriptId: str, currentUser: dict = Depends(get_current_user)):
    """Generate audio files for all dialogue lines in a script"""
    try:
        logger.info(f"🎵 User {currentUser['email']} requesting audio generation for script: {scriptId}")
        
        # Get script from Firebase
        firebaseService = getFirebaseService()
        script = firebaseService.getScript(scriptId)
        
        if not script:
            logger.warning(f"❌ Script '{scriptId}' not found for user {currentUser['email']}")
            raise HTTPException(status_code=404, detail=f"Script '{scriptId}' not found")
        
        dialogueLines = script.get("dialogue", [])
        
        if not dialogueLines:
            logger.warning(f"❌ Script '{scriptId}' has no dialogue lines for user {currentUser['email']}")
            raise HTTPException(status_code=400, detail="Script has no dialogue lines")
        
        # Check ownership for logging
        isOwner = script.get("createdBy") == currentUser['id']
        ownerInfo = " (Your script)" if isOwner else f" (Owner: {script.get('createdByName', 'Unknown')})"
        
        logger.info(f"🎤 Starting audio generation for script {scriptId}{ownerInfo} with {len(dialogueLines)} dialogue lines")
        
        # Load required data for audio generation
        scriptsData = firebaseService.getAllScripts()
        userProfiles = loadUserProfiles(USER_PROFILES_FILE)
        
        # Generate audio files
        result = await generateAudioForScript(
            scriptId, scriptsData, userProfiles, GENERATED_AUDIO_DIR, None
        )
        
        # Save updated scripts data back to Firebase
        firebaseService.saveScripts(scriptsData)
        
        logger.info(f"✅ Audio generation completed for script {scriptId} for user {currentUser['email']}: {result.message}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Audio generation failed for script {scriptId} for user {currentUser['email']}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Audio generation failed: {str(e)}")

@app.get("/api/f5tts/status")
async def get_f5tts_status():
    try:
        is_connected = checkF5ttsConnection()
        return {
            "status": "connected" if is_connected else "disconnected",
            "url": F5TTS_URL,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"💥 Error checking F5-TTS status: {str(e)}")
        return {
            "status": "error",
            "url": F5TTS_URL,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/scripts/{scriptId}/generate-video", response_model=VideoGenerationJobResponse)
async def generateScriptVideo(scriptId: str, currentUser: dict = Depends(get_current_user), backgroundVideo: Optional[str] = None):
    try:
        logger.info(f"🎬 User {currentUser['email']} requesting video generation for script: {scriptId}")
        
        # Get script from Firebase
        firebaseService = getFirebaseService()
        script = firebaseService.getScript(scriptId)
        
        if not script:
            logger.warning(f"❌ Script '{scriptId}' not found for user {currentUser['email']}")
            raise HTTPException(status_code=404, detail=f"Script '{scriptId}' not found")
        
        dialogueLines = script.get("dialogue", [])
        
        if not dialogueLines:
            logger.warning(f"❌ Script '{scriptId}' has no dialogue lines for user {currentUser['email']}")
            raise HTTPException(status_code=400, detail="Script has no dialogue lines")
        
        # Check ownership for logging
        isOwner = script.get("createdBy") == currentUser['id']
        ownerInfo = " (Your script)" if isOwner else f" (Owner: {script.get('createdByName', 'Unknown')})"
        
        logger.info(f"🎥 Queuing video generation for script {scriptId}{ownerInfo} with {len(dialogueLines)} dialogue lines")
        
        # Queue video generation job
        backgroundService = get_background_video_service()
        jobId = await backgroundService.queue_video_generation(
            scriptId, currentUser['id'], backgroundVideo
        )
        
        # Get the created job
        job_data = firebaseService.getVideoGenerationJob(jobId)
        if not job_data:
            raise HTTPException(status_code=500, detail="Failed to create video generation job")
        
        # Log video generation start activity
        firebaseService.addVideoActivity(
            currentUser['id'], 
            firebaseService.ActivityType.VIDEO_GENERATION_STARTED, 
            scriptId, 
            script.get("originalPrompt", "")[:50] + "..." if len(script.get("originalPrompt", "")) > 50 else script.get("originalPrompt", scriptId)
        )
        
        logger.info(f"✅ Video generation job queued for script {scriptId} for user {currentUser['email']} (Job ID: {jobId})")
        
        # Convert to Pydantic model
        job = VideoGenerationJob(**job_data)
        
        return VideoGenerationJobResponse(
            job=job,
            message=f"Video generation started successfully! Job ID: {jobId}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Video generation failed for script {scriptId} for user {currentUser['email']}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")

@app.get("/api/scripts/{scriptId}/video-status", response_model=VideoGenerationStatus)
async def getVideoGenerationStatus(scriptId: str, currentUser: dict = Depends(get_current_user)):
    try:
        logger.info(f"🎬 User {currentUser['email']} checking video status for script: {scriptId}")
        
        # Get script from Firebase
        firebaseService = getFirebaseService()
        script = firebaseService.getScript(scriptId)
        
        if not script:
            logger.warning(f"❌ Script '{scriptId}' not found for user {currentUser['email']}")
            raise HTTPException(status_code=404, detail=f"Script '{scriptId}' not found")
        
        finalVideoPath = script.get("finalVideoPath", "")
        
        # Check ownership for logging
        isOwner = script.get("createdBy") == currentUser['id']
        ownerInfo = " (Your script)" if isOwner else f" (Owner: {script.get('createdByName', 'Unknown')})"
        
        # Check if video exists and is valid
        if finalVideoPath and os.path.exists(finalVideoPath) and os.path.getsize(finalVideoPath) > 0:
            status = "completed"
            message = f"Video generated successfully: {os.path.basename(finalVideoPath)}"
            progress = 100.0
            logger.info(f"✅ Video completed for script {scriptId}{ownerInfo}: {os.path.basename(finalVideoPath)}")
        else:
            # Check audio readiness
            dialogueLines = script.get("dialogue", [])
            totalLines = len(dialogueLines)
            audioLines = 0
            
            for line in dialogueLines:
                audioFile = line.get("audioFile", "")
                if audioFile and os.path.exists(audioFile):
                    audioLines += 1
            
            if audioLines == totalLines and totalLines > 0:
                status = "pending"
                message = f"Ready for video generation ({audioLines}/{totalLines} audio files ready)"
                progress = 0.0
                logger.info(f"⏳ Script {scriptId}{ownerInfo} ready for video generation")
            else:
                status = "pending"
                message = f"Waiting for audio generation ({audioLines}/{totalLines} audio files ready)"
                progress = 0.0
                logger.info(f"⏳ Script {scriptId}{ownerInfo} waiting for audio: {audioLines}/{totalLines} files ready")
        
        return VideoGenerationStatus(
            scriptId=scriptId,
            status=status,
            stage="ready" if status == "pending" else "completed",
            progress=progress,
            message=message,
            finalVideoPath=finalVideoPath if finalVideoPath else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Failed to get video status for script {scriptId} for user {currentUser['email']}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get video status: {str(e)}")

@app.get("/api/system/ffmpeg-status")
async def check_ffmpeg_status():
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

@app.get("/api/test-image-serving")
async def test_image_serving():
    """Test endpoint to verify image serving configuration"""
    try:
        images_dir = os.path.abspath(IMAGES_DIR)
        test_files = []
        
        if os.path.exists(images_dir):
            for file in os.listdir(images_dir)[:5]:  # Get first 5 files as examples
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    local_path = os.path.join(images_dir, file)
                    relative_path = f"images/{file}"
                    url = f"/api/static/{relative_path}"
                    
                    test_files.append({
                        "filename": file,
                        "localPath": local_path,
                        "url": url,
                        "exists": os.path.exists(local_path)
                    })
        
        return {
            "message": "Image serving test endpoint",
            "imagesDirectory": images_dir,
            "staticMount": "/api/static",
            "sampleFiles": test_files,
            "instructions": "Images should be accessible at /api/static/images/filename.ext"
        }
    except Exception as e:
        logger.error(f"💥 Error in test endpoint: {str(e)}")
        return {"error": str(e)}

@app.get("/api/my-characters", response_model=List[CharacterResponse])
async def get_my_characters(request: Request, current_user: dict = Depends(get_current_user)):
    """Get all characters created by the current user"""
    try:
        firebase_service = getFirebaseService()
        user_characters = firebase_service.getUserCharacters(current_user['id'])
        
        characters = []
        for char_data in user_characters:
            char_id = char_data['id']
            character = build_character_response(char_id, char_data, request, current_user)
            characters.append(character)
        
        logger.info(f"📄 Retrieved {len(characters)} characters for user {current_user['id']}")
        return characters
    except Exception as e:
        logger.error(f"💥 Error getting user characters: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get user's characters: {str(e)}")

@app.get("/api/my-scripts", response_model=List[ScriptResponse])
async def getMyScripts(currentUser: dict = Depends(get_current_user)):
    """Get all scripts created by the current user with embedded video job information"""
    try:
        logger.info(f"📝 User {currentUser['email']} requesting their own scripts")
        
        # Get user's scripts from Firebase
        firebaseService = getFirebaseService()
        userScripts = firebaseService.getUserScripts(currentUser['id'])
        
        scriptResponses = []
        
        for scriptData in userScripts:
            dialogueLines = scriptData.get("dialogue", [])
            
            # Count audio files that exist
            audioCount = 0
            for dialogueLine in dialogueLines:
                audioFile = dialogueLine.get("audioFile", "")
                if audioFile and os.path.exists(audioFile):
                    audioCount += 1
            
            # **NEW**: Add video job information to the script response
            scriptResponse = ScriptResponse(
                id=scriptData["id"],
                selectedCharacters=scriptData["selectedCharacters"],
                originalPrompt=scriptData["originalPrompt"],
                dialogue=dialogueLines,
                createdAt=scriptData["createdAt"],
                updatedAt=scriptData["updatedAt"],
                hasAudio=audioCount > 0,
                audioCount=audioCount,
                finalVideoPath=scriptData.get("finalVideoPath"),
                videoDuration=scriptData.get("videoDuration"),
                videoSize=scriptData.get("videoSize"),
                # Video job information embedded directly in script
                videoJobId=scriptData.get("currentVideoJobId"),
                videoJobStatus=scriptData.get("videoJobStatus"),
                videoJobProgress=scriptData.get("videoJobProgress", 0.0),
                videoJobCurrentStep=scriptData.get("videoJobCurrentStep"),
                videoJobStartedAt=scriptData.get("videoJobStartedAt"),
                videoJobCompletedAt=scriptData.get("videoJobCompletedAt"),
                videoJobErrorMessage=scriptData.get("videoJobErrorMessage")
            )
            scriptResponses.append(scriptResponse)
        
        logger.info(f"📊 Retrieved {len(scriptResponses)} scripts for user {currentUser['email']}")
        return scriptResponses
        
    except Exception as e:
        logger.error(f"💥 Failed to get user scripts for {currentUser['email']}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get user scripts: {str(e)}")

# Star/Favorite Endpoints

@app.post("/api/characters/{character_id}/star", response_model=StarResponse)
async def star_character(character_id: str, current_user: dict = Depends(get_current_user)):
    """Star a character and add to user's favorites"""
    try:
        logger.info(f"⭐ User {current_user['id']} attempting to star character {character_id}")
        
        firebase_service = getFirebaseService()
        
        # Star the character
        success, message, starred_count = firebase_service.starCharacter(character_id, current_user['id'])
        
        if not success:
            logger.warning(f"⚠️ Failed to star character {character_id}: {message}")
            if "already starred" in message.lower():
                raise HTTPException(status_code=409, detail=message)
            elif "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message)
            else:
                raise HTTPException(status_code=400, detail=message)
        
        # Log character starring activity
        char_data = firebase_service.getUserProfile(character_id)
        char_name = char_data.get("displayName", character_id) if char_data else character_id
        firebase_service.addCharacterActivity(
            current_user['id'], 
            firebase_service.ActivityType.CHARACTER_STARRED, 
            character_id, 
            char_name
        )
        
        logger.info(f"✅ Character {character_id} starred by user {current_user['id']}")
        
        return StarResponse(
            success=True,
            message=message,
            characterId=character_id,
            starred=starred_count,
            isStarred=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error starring character: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to star character: {str(e)}")

@app.delete("/api/characters/{character_id}/star", response_model=StarResponse)
async def unstar_character(character_id: str, current_user: dict = Depends(get_current_user)):
    """Unstar a character and remove from user's favorites"""
    try:
        logger.info(f"⭐ User {current_user['id']} attempting to unstar character {character_id}")
        
        firebase_service = getFirebaseService()
        
        # Unstar the character
        success, message, starred_count = firebase_service.unstarCharacter(character_id, current_user['id'])
        
        if not success:
            logger.warning(f"⚠️ Failed to unstar character {character_id}: {message}")
            if "not starred" in message.lower():
                raise HTTPException(status_code=409, detail=message)
            elif "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message)
            else:
                raise HTTPException(status_code=400, detail=message)
        
        # Log character unstarring activity
        char_data = firebase_service.getUserProfile(character_id)
        char_name = char_data.get("displayName", character_id) if char_data else character_id
        firebase_service.addCharacterActivity(
            current_user['id'], 
            firebase_service.ActivityType.CHARACTER_UNSTARRED, 
            character_id, 
            char_name
        )
        
        logger.info(f"✅ Character {character_id} unstarred by user {current_user['id']}")
        
        return StarResponse(
            success=True,
            message=message,
            characterId=character_id,
            starred=starred_count,
            isStarred=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error unstarring character: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to unstar character: {str(e)}")

@app.get("/api/my-favorites", response_model=List[CharacterResponse])
async def get_my_favorite_characters(request: Request, current_user: dict = Depends(get_current_user)):
    """Get all favorite characters for the current user"""
    try:
        logger.info(f"📋 Getting favorite characters for user {current_user['id']}")
        
        firebase_service = getFirebaseService()
        
        # Get favorite characters data
        favorite_chars_data = firebase_service.getUserFavoriteCharacters(current_user['id'])
        
        # Build response list
        response_list = []
        for char_data in favorite_chars_data:
            char_id = char_data.get('id')
            if char_id:
                character_response = build_character_response(char_id, char_data, request, current_user)
                response_list.append(character_response)
        
        logger.info(f"✅ Retrieved {len(response_list)} favorite characters for user {current_user['id']}")
        return response_list
        
    except Exception as e:
        logger.error(f"💥 Error getting favorite characters: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get favorite characters: {str(e)}")

# User Activity Endpoints

@app.get("/api/my-activities", response_model=UserActivityResponse)
async def get_my_activities(current_user: dict = Depends(get_current_user), limit: int = 50):
    """Get current user's activity log"""
    try:
        logger.info(f"📋 Getting activities for user {current_user['id']} (limit: {limit})")
        
        firebase_service = getFirebaseService()
        activities_data = firebase_service.getUserActivities(current_user['id'], limit)
        
        # Convert to UserActivity models
        activities = []
        for activity_data in activities_data:
            activity = UserActivity(
                id=activity_data.get('id', ''),
                type=activity_data.get('type', ''),
                message=activity_data.get('message', ''),
                timestamp=convert_datetime_to_string(activity_data.get('timestamp', '')),
                scriptId=activity_data.get('scriptId'),
                characterId=activity_data.get('characterId'),
                videoPath=activity_data.get('videoPath')
            )
            activities.append(activity)
        
        logger.info(f"✅ Retrieved {len(activities)} activities for user {current_user['id']}")
        
        return UserActivityResponse(
            activities=activities,
            totalCount=len(activities),
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"💥 Error getting user activities: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get user activities: {str(e)}")

@app.get("/api/my-activity-stats", response_model=ActivityStats)
async def get_my_activity_stats(current_user: dict = Depends(get_current_user)):
    """Get current user's activity statistics"""
    try:
        logger.info(f"📊 Getting activity stats for user {current_user['id']}")
        
        firebase_service = getFirebaseService()
        activities_data = firebase_service.getUserActivities(current_user['id'], limit=None)  # Get all activities
        
        script_activities = 0
        character_activities = 0
        video_activities = 0
        last_activity_at = None
        
        for activity in activities_data:
            activity_type = activity.get('type', '')
            
            if activity_type.startswith('script_'):
                script_activities += 1
            elif activity_type.startswith('character_'):
                character_activities += 1
            elif activity_type.startswith('video_'):
                video_activities += 1
            
            # Get the most recent activity timestamp
            timestamp = convert_datetime_to_string(activity.get('timestamp', ''))
            if not last_activity_at or (timestamp > last_activity_at):
                last_activity_at = timestamp
        
        total_activities = len(activities_data)
        
        logger.info(f"✅ Activity stats for user {current_user['id']}: {total_activities} total activities")
        
        return ActivityStats(
            scriptActivities=script_activities,
            characterActivities=character_activities,
            videoActivities=video_activities,
            totalActivities=total_activities,
            lastActivityAt=last_activity_at
        )
        
    except Exception as e:
        logger.error(f"💥 Error getting activity stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get activity stats: {str(e)}")

@app.delete("/api/my-activities")
async def clear_my_activities(current_user: dict = Depends(get_current_user)):
    """Clear all activities for the current user"""
    try:
        logger.info(f"🗑️ Clearing activities for user {current_user['id']}")
        
        firebase_service = getFirebaseService()
        success = firebase_service.clearUserActivities(current_user['id'])
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to clear activities")
        
        logger.info(f"✅ Cleared activities for user {current_user['id']}")
        
        return {
            "message": "All activities cleared successfully",
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error clearing activities: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear activities: {str(e)}")

@app.get("/api/video-jobs/{jobId}", response_model=VideoGenerationJob)
async def getVideoGenerationJob(jobId: str, currentUser: dict = Depends(get_current_user)):
    """Get detailed information about a video generation job"""
    try:
        logger.info(f"📋 User {currentUser['email']} requesting video job details: {jobId}")
        
        firebaseService = getFirebaseService()
        job_data = firebaseService.getVideoGenerationJob(jobId)
        
        if not job_data:
            logger.warning(f"❌ Video job '{jobId}' not found for user {currentUser['email']}")
            raise HTTPException(status_code=404, detail=f"Video generation job '{jobId}' not found")
        
        # Check if user owns this job
        if job_data.get('userId') != currentUser['id']:
            logger.warning(f"🚫 User {currentUser['email']} denied access to video job {jobId}")
            raise HTTPException(status_code=403, detail="Access denied. You can only view your own video generation jobs.")
        
        logger.info(f"✅ Retrieved video job {jobId} for user {currentUser['email']} (Status: {job_data.get('status')})")
        
        return VideoGenerationJob(**job_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error getting video job {jobId} for user {currentUser['email']}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get video generation job: {str(e)}")

@app.get("/api/my-video-jobs", response_model=List[VideoGenerationJob])
async def getMyVideoGenerationJobs(currentUser: dict = Depends(get_current_user), limit: int = 10):
    """Get all video generation jobs for the current user"""
    try:
        logger.info(f"📋 User {currentUser['email']} requesting their video generation jobs (limit: {limit})")
        
        firebaseService = getFirebaseService()
        jobs_data = firebaseService.getUserVideoGenerationJobs(currentUser['id'], limit)
        
        jobs = [VideoGenerationJob(**job_data) for job_data in jobs_data]
        
        logger.info(f"✅ Retrieved {len(jobs)} video generation jobs for user {currentUser['email']}")
        return jobs
        
    except Exception as e:
        logger.error(f"💥 Error getting user video jobs for {currentUser['email']}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get video generation jobs: {str(e)}")

@app.get("/api/scripts/{scriptId}/video-job", response_model=VideoGenerationJob)
async def getScriptVideoJob(scriptId: str, currentUser: dict = Depends(get_current_user)):
    """Get the most recent video generation job for a specific script"""
    try:
        logger.info(f"🎬 User {currentUser['email']} requesting video job for script: {scriptId}")
        
        firebaseService = getFirebaseService()
        
        # Get user's video jobs and filter by script
        jobs_data = firebaseService.getUserVideoGenerationJobs(currentUser['id'], 50)  # Get more to find script job
        
        script_jobs = [job for job in jobs_data if job.get('scriptId') == scriptId]
        
        if not script_jobs:
            logger.warning(f"❌ No video job found for script '{scriptId}' for user {currentUser['email']}")
            raise HTTPException(status_code=404, detail=f"No video generation job found for script '{scriptId}'")
        
        # Get the most recent job (first in the list since they're ordered by creation date desc)
        latest_job = script_jobs[0]
        
        logger.info(f"✅ Retrieved video job for script {scriptId} for user {currentUser['email']} (Status: {latest_job.get('status')})")
        
        return VideoGenerationJob(**latest_job)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error getting video job for script {scriptId} for user {currentUser['email']}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get video generation job for script: {str(e)}")

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