import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from fastapi import UploadFile, HTTPException
from models import CharacterConfig
from firebase_service import get_firebase_service

logger = logging.getLogger(__name__)

def loadUserProfiles(userProfilesFile: str = None) -> Dict[str, Any]:
    try:
        firebase_service = get_firebase_service()
        profiles_data = firebase_service.get_all_user_profiles()
        
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
            firebase_service.save_user_profiles(defaultData)
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
        
        return profiles_data
    except Exception as e:
        logger.error(f"💥 Failed to load user profiles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to load user profiles: {str(e)}")

def saveUserProfiles(data: Dict[str, Any], userProfilesFile: str = None) -> None:
    try:
        firebase_service = get_firebase_service()
        success = firebase_service.save_user_profiles(data)
        
        if not success:
            raise Exception("Failed to save user profiles to Firebase")
            
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

def loadScripts(scriptsFile: str = None) -> Dict[str, Any]:
    try:
        firebase_service = get_firebase_service()
        scripts_data = firebase_service.get_all_scripts()
        
        if not scripts_data.get("scripts"):
            defaultData = {
                "scripts": {},
                "createdAt": datetime.now().isoformat()
            }
            firebase_service.save_scripts(defaultData)
            return defaultData
        
        if "createdAt" not in scripts_data:
            scripts_data["createdAt"] = datetime.now().isoformat()
        
        return scripts_data
    except Exception as e:
        logger.error(f"💥 Failed to load scripts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to load scripts: {str(e)}")

def saveScripts(data: Dict[str, Any], scriptsFile: str = None) -> None:
    try:
        firebase_service = get_firebase_service()
        success = firebase_service.save_scripts(data)
        
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