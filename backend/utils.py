import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import io
from fastapi import UploadFile, HTTPException
from models import CharacterConfig
from firebase_service import getFirebaseService
from PIL import Image

logger = logging.getLogger(__name__)

# Simple in-memory cache for user profiles
_user_profiles_cache: Optional[Dict[str, Any]] = None
_cache_timestamp: Optional[datetime] = None
CACHE_DURATION_MINUTES = 5  # Cache for 5 minutes

def _is_cache_valid() -> bool:
    """Check if the cache is still valid"""
    if _user_profiles_cache is None or _cache_timestamp is None:
        return False
    
    return datetime.now() - _cache_timestamp < timedelta(minutes=CACHE_DURATION_MINUTES)

def _clear_cache():
    """Clear the cache"""
    global _user_profiles_cache, _cache_timestamp
    _user_profiles_cache = None
    _cache_timestamp = None

def loadUserProfiles(userProfilesFile: str = None) -> Dict[str, Any]:
    global _user_profiles_cache, _cache_timestamp
    
    try:
        # Return cached data if available and valid
        if _is_cache_valid():
            logger.debug(f"📋 Using cached user profiles ({len(_user_profiles_cache.get('users', {}))} profiles)")
            return _user_profiles_cache
        
        firebase_service = getFirebaseService()
        profiles_data = firebase_service.getAllUserProfiles()
        
        if not profiles_data.get("users"):
            defaultData = {
                "default": {
                    "speed": 1.0,
                    "nfeSteps": 34,
                    "crossFadeDuration": 0.15,
                    "removeSilences": True,
                    "f5ttsUrl": "http://localhost:7860",
                    "timeoutSeconds": 300,
                    "downloadDirectory": "apiData/audio_files/generated",
                    "defaultAudioFile": "apiData/audio_files/default.wav",
                    "defaultOutputPrefix": "defaultGenerated"
                },
                "users": {},
                "defaultUser": None,
                "createdAt": datetime.now().isoformat() + 'Z'
            }
            firebase_service.saveUserProfiles(defaultData)
            
            # Cache the default data
            _user_profiles_cache = defaultData
            _cache_timestamp = datetime.now()
            return defaultData
        
        if "default" not in profiles_data:
            profiles_data["default"] = {
                "speed": 1.0,
                "nfeSteps": 34,
                "crossFadeDuration": 0.15,
                "removeSilences": True,
                "f5ttsUrl": "http://localhost:7860",
                "timeoutSeconds": 300,
                "downloadDirectory": "apiData/audio_files/generated",
                "defaultAudioFile": "apiData/audio_files/default.wav",
                "defaultOutputPrefix": "defaultGenerated"
            }
        
        # Cache the profiles data
        _user_profiles_cache = profiles_data
        _cache_timestamp = datetime.now()
        logger.info(f"📋 Loaded and cached {len(profiles_data.get('users', {}))} user profiles")
        
        return profiles_data
    except Exception as e:
        logger.error(f"💥 Failed to load user profiles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to load user profiles: {str(e)}")

def saveUserProfiles(data: Dict[str, Any], userProfilesFile: str = None) -> None:
    try:
        firebase_service = getFirebaseService()
        success = firebase_service.saveUserProfiles(data)
        
        if not success:
            raise Exception("Failed to save user profiles to Firebase")
        
        # Clear cache after saving to ensure fresh data on next load
        _clear_cache()
        logger.info("🗑️ Cleared user profiles cache after save")
            
    except Exception as e:
        logger.error(f"💥 Failed to save user profiles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save user profiles: {str(e)}")

def generateCharacterId(displayName: str, userProfilesFile: str) -> str:
    baseId = displayName.lower().replace(' ', '').replace('-', '').replace('_', '')
    profiles = loadUserProfiles(userProfilesFile)
    existingIds = set(profiles.get("users", {}).keys())
    
    if baseId not in existingIds:
        return baseId
    
    counter = 1
    while f"{baseId}{counter}" in existingIds:
        counter += 1
    
    return f"{baseId}{counter}"

def getDefaultConfig(userProfilesFile: str) -> CharacterConfig:
    try:
        profiles = loadUserProfiles(userProfilesFile)
        defaultConfig = profiles.get("default", {})
        
        return CharacterConfig(
            speed=defaultConfig.get("speed", 1.0),
            nfeSteps=defaultConfig.get("nfeSteps", 34),
            crossFadeDuration=defaultConfig.get("crossFadeDuration", 0.15),
            removeSilences=defaultConfig.get("removeSilences", True)
        )
    except Exception:
        return CharacterConfig()

def validateAudioFile(file: UploadFile) -> bool:
    allowedExtensions = {'.wav', '.mp3', '.m4a', '.flac', '.ogg'}
    fileExt = Path(file.filename).suffix.lower()
    
    if fileExt not in allowedExtensions:
        return False
    
    if file.size and file.size > 50 * 1024 * 1024:
        return False
    
    return True

def validateImageFile(file: UploadFile) -> bool:
    allowedExtensions = {'.png', '.jpg', '.jpeg', '.webp'}
    fileExt = Path(file.filename).suffix.lower()
    
    if fileExt not in allowedExtensions:
        return False
    
    if file.size and file.size > 10 * 1024 * 1024:
        return False
    
    return True


def trimImageTransparency(image_file: UploadFile) -> bytes:
    """
    Trim transparent/blank areas from uploaded image and return cropped image bytes.
    
    Args:
        image_file: UploadFile containing the image
        
    Returns:
        bytes: Cropped image data in PNG format
    """
    try:
        # Read the uploaded file content
        image_content = image_file.file.read()
        image_file.file.seek(0)  # Reset file pointer for potential re-reading
        
        # Open image with PIL
        image = Image.open(io.BytesIO(image_content))
        
        # Convert to RGBA if not already (to handle transparency)
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Get the bounding box of non-transparent pixels
        # getbbox() returns (left, top, right, bottom) of the non-zero pixels
        bbox = image.getbbox()
        
        if bbox is None:
            # Image is completely transparent, return original
            logger.warning("⚠️ Image is completely transparent, returning original")
            return image_content
        
        # Crop the image to the bounding box
        cropped_image = image.crop(bbox)
        
        # Convert back to bytes
        output_buffer = io.BytesIO()
        cropped_image.save(output_buffer, format='PNG', optimize=True)
        cropped_bytes = output_buffer.getvalue()
        
        # Log the trimming results
        original_size = image.size
        cropped_size = cropped_image.size
        size_reduction = ((original_size[0] * original_size[1] - cropped_size[0] * cropped_size[1]) / 
                         (original_size[0] * original_size[1])) * 100
        
        logger.info(f"✂️ Image trimmed: {original_size} → {cropped_size} ({size_reduction:.1f}% reduction)")
        
        return cropped_bytes
        
    except Exception as e:
        logger.error(f"❌ Error trimming image: {str(e)}")
        # Return original content if trimming fails
        image_file.file.seek(0)
        return image_file.file.read()

def loadScripts(scriptsFile: str = None) -> Dict[str, Any]:
    try:
        firebase_service = getFirebaseService()
        scripts_data = firebase_service.getAllScripts()
        
        if not scripts_data.get("scripts"):
            defaultData = {
                "scripts": {},
                "createdAt": datetime.now().isoformat()
            }
            firebase_service.saveScripts(defaultData)
            return defaultData
        
        if "createdAt" not in scripts_data:
            scripts_data["createdAt"] = datetime.now().isoformat()
        
        return scripts_data
    except Exception as e:
        logger.error(f"💥 Failed to load scripts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to load scripts: {str(e)}")

def saveScripts(data: Dict[str, Any], scriptsFile: str = None) -> None:
    try:
        firebase_service = getFirebaseService()
        success = firebase_service.saveScripts(data)
        
        if not success:
            raise Exception("Failed to save scripts to Firebase")
            
    except Exception as e:
        logger.error(f"💥 Failed to save scripts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save scripts: {str(e)}")

def generateScriptId() -> str:
    import uuid
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shortUuid = str(uuid.uuid4())[:8]
    return f"script_{timestamp}_{shortUuid}" 