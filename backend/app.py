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
    SignupRequest, LoginRequest, UserResponse, AuthResponse
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
from firebase_service import initialize_firebase_service, get_firebase_service
from jwt_service import get_jwt_service

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
    firebase_service = initialize_firebase_service("firebase.json")
    print("🔥 Firebase initialized successfully!")
except Exception as e:
    print(f"❌ Firebase initialization failed: {str(e)}")
    raise

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

# JWT Authentication
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """JWT authentication dependency"""
    try:
        token = credentials.credentials
        jwt_service = get_jwt_service()
        
        payload = jwt_service.verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user data from Firebase
        firebase_service = get_firebase_service()
        user_data = firebase_service.get_user_by_id(payload['user_id'])
        
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

# Helper functions for converting file paths to URLs
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
        firebase_service = get_firebase_service()
        
        # Create user in Firebase Auth and Firestore
        success, message, user_id = firebase_service.create_user(
            request.email, 
            request.password, 
            request.name
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        # Get user data from Firestore
        user_data = firebase_service.get_user_by_id(user_id)
        if not user_data:
            raise HTTPException(status_code=500, detail="Failed to retrieve user data after creation")
        
        # Create JWT token
        jwt_service = get_jwt_service()
        token, expires_in = jwt_service.create_token(user_id, request.email)
        
        # Create user response
        user_response = UserResponse(
            id=user_data['id'],
            name=user_data['name'],
            email=user_data['email'],
            isVerified=user_data['isVerified'],
            subscription=user_data['subscription'],
            createdAt=user_data['createdAt'],
            updatedAt=user_data['updatedAt']
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
        firebase_service = get_firebase_service()
        
        # Verify user credentials (email and password)
        success, message, user_id = firebase_service.verify_user_password(request.email, request.password)
        if not success:
            logger.warning(f"🔒 Login failed for {request.email}: {message}")
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Get user data from Firestore
        user_data = firebase_service.get_user_by_id(user_id)
        if not user_data:
            raise HTTPException(status_code=500, detail="Failed to retrieve user data")
        
        # Create JWT token
        jwt_service = get_jwt_service()
        token, expires_in = jwt_service.create_token(user_id, request.email)
        
        # Create user response
        user_response = UserResponse(
            id=user_data['id'],
            name=user_data['name'],
            email=user_data['email'],
            isVerified=user_data['isVerified'],
            subscription=user_data['subscription'],
            createdAt=user_data['createdAt'],
            updatedAt=user_data['updatedAt']
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
            createdAt=current_user['createdAt'],
            updatedAt=current_user['updatedAt']
        )
    except Exception as e:
        logger.error(f"💥 Error getting user profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user profile")

@app.post("/api/refresh-token", response_model=AuthResponse)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Refresh JWT token"""
    try:
        old_token = credentials.credentials
        jwt_service = get_jwt_service()
        
        result = jwt_service.refresh_token(old_token)
        if not result:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        new_token, expires_in = result
        
        # Get user data from the old token
        payload = jwt_service.decode_token_without_verification(old_token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token format")
        
        firebase_service = get_firebase_service()
        user_data = firebase_service.get_user_by_id(payload['user_id'])
        
        if not user_data:
            raise HTTPException(status_code=401, detail="User not found")
        
        user_response = UserResponse(
            id=user_data['id'],
            name=user_data['name'],
            email=user_data['email'],
            isVerified=user_data['isVerified'],
            subscription=user_data['subscription'],
            createdAt=user_data['createdAt'],
            updatedAt=user_data['updatedAt']
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
            audio_file = char_data.get("audioFile", "")
            has_audio = bool(audio_file and os.path.exists(audio_file))
            
            # Convert local file paths to URLs
            audio_url = convert_local_path_to_url(audio_file, request)
            images = char_data.get("images", {})
            images_urls = convert_images_dict_to_urls(images, request)
            image_count = len(images)
            
            config_data = char_data.get("config", {})
            default_config = getDefaultConfig(USER_PROFILES_FILE)
            
            config = CharacterConfig(
                speed=config_data.get("speed", default_config.speed),
                nfeSteps=config_data.get("nfeSteps", default_config.nfeSteps),
                crossFadeDuration=config_data.get("crossFadeDuration", default_config.crossFadeDuration),
                removeSilences=config_data.get("removeSilences", default_config.removeSilences)
            )
            
            character = CharacterResponse(
                id=char_id,
                displayName=char_data.get("displayName", char_id.title()),
                audioFile=audio_url,
                config=config,
                images=images_urls,
                outputPrefix=char_data.get("outputPrefix", char_id),
                createdAt=char_data.get("createdAt", datetime.now().isoformat()),
                updatedAt=char_data.get("updatedAt", datetime.now().isoformat()),
                hasAudio=has_audio,
                imageCount=image_count
            )
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
        
        audio_file = char_data.get("audioFile", "")
        has_audio = bool(audio_file and os.path.exists(audio_file))
        
        # Convert local file paths to URLs
        audio_url = convert_local_path_to_url(audio_file, request)
        images = char_data.get("images", {})
        images_urls = convert_images_dict_to_urls(images, request)
        image_count = len(images)
        
        config_data = char_data.get("config", {})
        default_config = getDefaultConfig(USER_PROFILES_FILE)
        
        config = CharacterConfig(
            speed=config_data.get("speed", default_config.speed),
            nfeSteps=config_data.get("nfeSteps", default_config.nfeSteps),
            crossFadeDuration=config_data.get("crossFadeDuration", default_config.crossFadeDuration),
            removeSilences=config_data.get("removeSilences", default_config.removeSilences)
        )
        
        return CharacterResponse(
            id=character_id,
            displayName=char_data.get("displayName", character_id.title()),
            audioFile=audio_url,
            config=config,
            images=images_urls,
            outputPrefix=char_data.get("outputPrefix", character_id),
            createdAt=char_data.get("createdAt", datetime.now().isoformat()),
            updatedAt=char_data.get("updatedAt", datetime.now().isoformat()),
            hasAudio=has_audio,
            imageCount=image_count
        )
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
        firebase_service = get_firebase_service()
        char_data = firebase_service.get_user_profile(character_id)
        
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
        success = firebase_service.update_character_with_owner_check(
            character_id, 
            update_data, 
            current_user['id']
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update character")
        
        logger.info(f"✅ Updated character: {character_id}")
        
        return await get_character(character_id, request)
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
        firebase_service = get_firebase_service()
        char_data = firebase_service.get_user_profile(character_id)
        
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
        success = firebase_service.delete_character_with_owner_cleanup(character_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete character from database")
        
        # Handle default user update if needed
        profiles = firebase_service.get_all_user_profiles()
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
            firebase_service = get_firebase_service()
            success = firebase_service.create_character_with_owner(
                character_id, 
                char_data, 
                current_user['id']
            )
            
            if not success:
                raise Exception("Failed to save character with ownership tracking")
            
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
        
        # Convert local paths to URLs for response
        audio_url = convert_local_path_to_url(audio_path, request)
        images_urls = convert_images_dict_to_urls(images_dict, request)
        
        return CharacterResponse(
            id=character_id,
            displayName=displayName,
            audioFile=audio_url,
            config=config,
            images=images_urls,
            outputPrefix=character_id,
            createdAt=current_time,
            updatedAt=current_time,
            hasAudio=True,
            imageCount=len(images_dict)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error creating character: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/api/scripts/generate", response_model=ScriptResponse)
async def generate_script(request: ScriptRequest):
    try:
        logger.info(f"📝 Generating script for characters: {request.selectedCharacters}")
        
        profiles = loadUserProfiles(USER_PROFILES_FILE)
        users = profiles.get("users", {})
        
        for char_id in request.selectedCharacters:
            if char_id not in users:
                raise HTTPException(status_code=400, detail=f"Character '{char_id}' not found")
        
        dialogue_lines = await generateScriptWithOpenai(
            request.selectedCharacters, 
            request.prompt, 
            request.word
        )
        
        script_id = generateScriptId()
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
        
        scripts = loadScripts(SCRIPTS_FILE)
        scripts["scripts"][script_id] = script_data
        saveScripts(scripts, SCRIPTS_FILE)
        
        logger.info(f"✅ Generated script: {script_id}")
        
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
        logger.error(f"💥 Error generating script: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate script: {str(e)}")

@app.get("/api/scripts", response_model=List[ScriptResponse])
async def list_scripts():
    try:
        scripts_data = loadScripts(SCRIPTS_FILE)
        scripts = scripts_data.get("scripts", {})
        
        script_responses = []
        for script_data in scripts.values():
            dialogue_lines = script_data.get("dialogue", [])
            
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
                videoDuration=script_data.get("videoDuration"),
                videoSize=script_data.get("videoSize")
            )
            script_responses.append(script_response)
        
        return script_responses
        
    except Exception as e:
        logger.error(f"💥 Error listing scripts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scripts/{script_id}", response_model=ScriptResponse)
async def get_script(script_id: str):
    try:
        scripts_data = loadScripts(SCRIPTS_FILE)
        scripts = scripts_data.get("scripts", {})
        
        if script_id not in scripts:
            raise HTTPException(status_code=404, detail=f"Script '{script_id}' not found")
        
        script_data = scripts[script_id]
        dialogue_lines = script_data.get("dialogue", [])
        
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
            videoDuration=script_data.get("videoDuration"),
            videoSize=script_data.get("videoSize")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error getting script {script_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/scripts/{script_id}", response_model=ScriptResponse)
async def update_script(script_id: str, updates: ScriptUpdate):
    try:
        scripts_data = loadScripts(SCRIPTS_FILE)
        scripts = scripts_data.get("scripts", {})
        
        if script_id not in scripts:
            raise HTTPException(status_code=404, detail=f"Script '{script_id}' not found")
        
        script_data = scripts[script_id]
        old_dialogue = script_data.get("dialogue", [])
        new_dialogue_updates = updates.dialogue
        
        logger.info(f"📝 Updating script {script_id} with {len(new_dialogue_updates)} dialogue lines")
        
        updated_dialogue = []
        deleted_audio_files = []
        dialogue_changed = False
        
        for i, new_line in enumerate(new_dialogue_updates):
            old_line = old_dialogue[i] if i < len(old_dialogue) else None
            
            new_dialogue_line = {
                "speaker": new_line.speaker,
                "text": new_line.text,
                "audioFile": ""
            }
            
            if old_line:
                old_text = old_line.get("text", "").strip()
                old_speaker = old_line.get("speaker", "").strip()
                old_audio = old_line.get("audioFile", "")
                
                new_text = new_line.text.strip()
                new_speaker = new_line.speaker.strip()
                
                text_changed = old_text != new_text
                speaker_changed = old_speaker != new_speaker
                
                if text_changed or speaker_changed:
                    dialogue_changed = True
                    if old_audio and old_audio.strip() and os.path.exists(old_audio):
                        try:
                            os.remove(old_audio)
                            deleted_audio_files.append(old_audio)
                            logger.info(f"🗑️ Deleted audio file for changed line {i}: {old_audio}")
                        except Exception as e:
                            logger.warning(f"⚠️ Could not delete audio file {old_audio}: {str(e)}")
                    
                    logger.info(f"📝 Line {i} changed - {'text' if text_changed else ''}{'speaker' if speaker_changed else ''} - audio cleared")
                else:
                    if old_audio and old_audio.strip() and os.path.exists(old_audio):
                        new_dialogue_line["audioFile"] = old_audio
                        logger.info(f"✅ Line {i} unchanged - keeping existing audio: {old_audio}")
                    else:
                        logger.info(f"📝 Line {i} unchanged - no existing audio")
            else:
                dialogue_changed = True
                logger.info(f"➕ New line {i} added: {new_line.speaker} - {new_line.text[:30]}...")
            
            updated_dialogue.append(new_dialogue_line)
        
        if len(old_dialogue) > len(new_dialogue_updates):
            dialogue_changed = True
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
        
        script_data["dialogue"] = updated_dialogue
        script_data["updatedAt"] = datetime.now().isoformat()
        
        if dialogue_changed:
            logger.info("🎬 Clearing video data since dialogue was modified")
            script_data["finalVideoPath"] = None
            script_data["videoDuration"] = None
            script_data["videoSize"] = None
        
        saveScripts(scripts_data, SCRIPTS_FILE)
        
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
            videoDuration=script_data.get("videoDuration"),
            videoSize=script_data.get("videoSize")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error updating script {script_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/scripts/{script_id}")
async def delete_script(script_id: str):
    try:
        # Get script data before deletion
        firebase_service = get_firebase_service()
        script = firebase_service.get_script(script_id)
        
        if not script:
            raise HTTPException(status_code=404, detail=f"Script '{script_id}' not found")
        
        dialogue_lines = script.get("dialogue", [])
        deleted_audio_files = []
        
        # Delete audio files
        for dialogue_line in dialogue_lines:
            audio_path = dialogue_line.get("audioFile", "")
            if audio_path and os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                    deleted_audio_files.append(audio_path)
                    logger.info(f"🗑️ Deleted audio: {audio_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not delete audio {audio_path}: {str(e)}")
        
        # Delete video file if exists
        final_video_path = script.get("finalVideoPath", "")
        if final_video_path and os.path.exists(final_video_path):
            try:
                os.remove(final_video_path)
                deleted_audio_files.append(final_video_path)
                logger.info(f"🗑️ Deleted video: {final_video_path}")
            except Exception as e:
                logger.warning(f"⚠️ Could not delete video {final_video_path}: {str(e)}")
        
        # Delete from Firebase
        success = firebase_service.delete_script(script_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete script from database")
        
        logger.info(f"✅ Deleted script: {script_id}")
        
        return {
            "message": f"Script '{script_id}' deleted successfully",
            "deletedAudioFiles": deleted_audio_files
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error deleting script {script_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scripts/{script_id}/audio-status")
async def get_audio_generation_status(script_id: str):
    try:
        scripts_data = loadScripts(SCRIPTS_FILE)
        scripts = scripts_data.get("scripts", {})
        
        if script_id not in scripts:
            raise HTTPException(status_code=404, detail=f"Script '{script_id}' not found")
        
        script = scripts[script_id]
        dialogue_lines = script.get("dialogue", [])
        
        total_lines = len(dialogue_lines)
        completed_lines = 0
        
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
        logger.error(f"💥 Error getting audio status for script {script_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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

@app.post("/api/scripts/{script_id}/generate-video", response_model=VideoGenerationResponse)
async def generate_script_video(script_id: str, background_video: Optional[str] = None):
    try:
        logger.info(f"🎬 Video generation requested for script: {script_id}")
        
        scripts_data = loadScripts(SCRIPTS_FILE)
        scripts = scripts_data.get("scripts", {})
        
        if script_id not in scripts:
            raise HTTPException(status_code=404, detail=f"Script '{script_id}' not found")
        
        script = scripts[script_id]
        dialogue_lines = script.get("dialogue", [])
        
        if not dialogue_lines:
            raise HTTPException(status_code=400, detail="Script has no dialogue lines")
        
        # Load user profiles (needed for both audio and video generation)
        user_profiles = loadUserProfiles(USER_PROFILES_FILE)
        
        # Check for missing audio files
        missing_audio = []
        for i, line in enumerate(dialogue_lines):
            audio_file = line.get("audioFile", "")
            if not audio_file or not os.path.exists(audio_file):
                missing_audio.append(i)
        
        # Generate missing audio files if any
        if missing_audio:
            logger.info(f"🎤 Generating audio for {len(missing_audio)} missing lines before video generation...")
            
            try:
                audio_result = await generateAudioForScript(
                    script_id,
                    scripts_data,
                    user_profiles,
                    GENERATED_AUDIO_DIR
                )
                logger.info(f"🎵 Audio generation result: {audio_result.message}")
                
                # Save updated scripts data with audio information
                saveScripts(scripts_data, SCRIPTS_FILE)
                
                # Reload script data after audio generation
                script = scripts_data.get("scripts", {})[script_id]
                dialogue_lines = script.get("dialogue", [])
                
                # Verify all audio files are now available
                still_missing = []
                for i, line in enumerate(dialogue_lines):
                    audio_file = line.get("audioFile", "")
                    if not audio_file or not os.path.exists(audio_file):
                        still_missing.append(f"Line {i+1} ({line.get('speaker', 'unknown')})")
                
                if still_missing:
                    raise HTTPException(
                        status_code=500, 
                        detail=f"Failed to generate audio for {len(still_missing)} lines. Cannot proceed with video generation. Missing: {', '.join(still_missing[:3])}{'...' if len(still_missing) > 3 else ''}"
                    )
                
            except HTTPException as audio_error:
                logger.error(f"❌ Audio generation failed: {audio_error.detail}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Audio generation failed before video generation: {audio_error.detail}"
                )
        else:
            logger.info(f"✅ All audio files already exist: {len(dialogue_lines)} files ready")
        
        # Proceed with video generation
        video_generator = VideoGenerator()
        
        result = await video_generator.generateVideo(
            script_id, 
            scripts_data, 
            user_profiles,
            VIDEO_OUTPUT_DIR,
            BACKGROUND_DIR, 
            DEFAULT_BACKGROUND_VIDEO,
            FONT_PATH,
            background_video
        )
        
        # Save updated scripts data with video information
        saveScripts(scripts_data, SCRIPTS_FILE)
        
        logger.info(f"✅ Video generation completed for script: {script_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Video generation API error for script {script_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")

@app.get("/api/scripts/{script_id}/video-status", response_model=VideoGenerationStatus)
async def get_video_generation_status(script_id: str):
    try:
        scripts_data = loadScripts(SCRIPTS_FILE)
        scripts = scripts_data.get("scripts", {})
        
        if script_id not in scripts:
            raise HTTPException(status_code=404, detail=f"Script '{script_id}' not found")
        
        script = scripts[script_id]
        final_video_path = script.get("finalVideoPath", "")
        
        if final_video_path and os.path.exists(final_video_path) and os.path.getsize(final_video_path) > 0:
            status = "completed"
            message = f"Video generated successfully: {os.path.basename(final_video_path)}"
            progress = 100.0
        else:
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
        logger.error(f"💥 Error getting video status for script {script_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
        firebase_service = get_firebase_service()
        user_characters = firebase_service.get_user_characters(current_user['id'])
        
        characters = []
        for char_data in user_characters:
            char_id = char_data['id']
            
            # Check if files exist
            audio_file = char_data.get("audioFile", "")
            has_audio = bool(audio_file and os.path.exists(audio_file))
            
            # Convert local file paths to URLs
            audio_url = convert_local_path_to_url(audio_file, request)
            images = char_data.get("images", {})
            images_urls = convert_images_dict_to_urls(images, request)
            image_count = len(images)
            
            config_data = char_data.get("config", {})
            default_config = getDefaultConfig(USER_PROFILES_FILE)
            
            config = CharacterConfig(
                speed=config_data.get("speed", default_config.speed),
                nfeSteps=config_data.get("nfeSteps", default_config.nfeSteps),
                crossFadeDuration=config_data.get("crossFadeDuration", default_config.crossFadeDuration),
                removeSilences=config_data.get("removeSilences", default_config.removeSilences)
            )
            
            character = CharacterResponse(
                id=char_id,
                displayName=char_data.get("displayName", char_id.title()),
                audioFile=audio_url,
                config=config,
                images=images_urls,
                outputPrefix=char_data.get("outputPrefix", char_id),
                createdAt=char_data.get("createdAt", datetime.now().isoformat()),
                updatedAt=char_data.get("updatedAt", datetime.now().isoformat()),
                hasAudio=has_audio,
                imageCount=image_count
            )
            characters.append(character)
        
        logger.info(f"📄 Retrieved {len(characters)} characters for user {current_user['id']}")
        return characters
    except Exception as e:
        logger.error(f"💥 Error getting user characters: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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