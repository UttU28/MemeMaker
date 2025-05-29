#!/usr/bin/env python3
"""
Configuration Manager for F5-TTS Gradio API Automation
Handles loading and managing user profiles and default configurations
"""

import json
import os
from typing import Dict, Any, Optional
from datetime import datetime


class ConfigManager:
    """Manages configuration files and user profiles with camelCase naming"""
    
    def __init__(self, profilesDir: str = "data"):
        """
        Initialize the configuration manager
        
        Args:
            profilesDir: Directory containing configuration files
        """
        self.profilesDir = profilesDir
        self.userProfilesPath = os.path.join(profilesDir, "userProfiles.json")
        self._defaultConfig = None
        self._userProfiles = None
    
    def loadDefaultConfig(self) -> Dict[str, Any]:
        if self._defaultConfig is None:
            try:
                profiles = self.loadUserProfiles()
                self._defaultConfig = profiles.get("default", self._getDefaultConfigFallback())
            except Exception as e:
                print(f"❌ Error loading default config: {e}")
                self._defaultConfig = self._getDefaultConfigFallback()
        
        return self._defaultConfig.copy()
    
    def loadUserProfiles(self) -> Dict[str, Any]:
        if self._userProfiles is None:
            try:
                with open(self.userProfilesPath, 'r', encoding='utf-8') as file:
                    self._userProfiles = json.load(file)
            except FileNotFoundError:
                print(f"❌ User profiles file not found: {self.userProfilesPath}")
                self._userProfiles = {"users": {}, "default": self._getDefaultConfigFallback()}
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing user profiles: {e}")
                self._userProfiles = {"users": {}, "default": self._getDefaultConfigFallback()}
        
        return self._userProfiles.copy()
    
    def getUserProfile(self, userId: str) -> Optional[Dict[str, Any]]:
        profiles = self.loadUserProfiles()
        return profiles.get("users", {}).get(userId)
    
    def getUserConfig(self, userId: str) -> Dict[str, Any]:
        defaultConfig = self.loadDefaultConfig()
        userProfile = self.getUserProfile(userId)
        
        if userProfile and "config" in userProfile:
            mergedConfig = defaultConfig.copy()
            mergedConfig.update(userProfile["config"])
            return mergedConfig
        
        return defaultConfig
    
    def getAllUserIds(self) -> list:
        profiles = self.loadUserProfiles()
        return list(profiles.get("users", {}).keys())
    
    def updateLastUsed(self, userId: str) -> bool:
        try:
            profiles = self.loadUserProfiles()
            profiles["lastUsed"] = userId
            profiles["updatedAt"] = datetime.now().isoformat()
            
            with open(self.userProfilesPath, 'w', encoding='utf-8') as file:
                json.dump(profiles, file, indent=4, ensure_ascii=False)
            
            self._userProfiles = profiles
            return True
            
        except Exception as e:
            print(f"❌ Error updating last used user: {e}")
            return False
    
    def getDefaultUserId(self) -> str:
        profiles = self.loadUserProfiles()
        return profiles.get("defaultUser", "palki")
    
    def getLastUsedUserId(self) -> str:
        profiles = self.loadUserProfiles()
        return profiles.get("lastUsed", self.getDefaultUserId())
    
    def _getDefaultConfigFallback(self) -> Dict[str, Any]:
        return {
            "speed": 1,
            "nfeSteps": 34,
            "crossFadeDuration": 0.15,
            "removeSilences": True,
            "f5ttsUrl": "http://localhost:7860",
            "timeoutSeconds": 300,
            "downloadDirectory": "audio_files/generated",
            "defaultAudioFile": "audio_files/Palki.wav",
            "defaultOutputPrefix": "defaultGenerated"
        }
    
    def validateUserProfile(self, userId: str) -> bool:
        userProfile = self.getUserProfile(userId)
        if not userProfile:
            return False
        
        requiredFields = ["displayName", "audioFile", "outputPrefix"]
        return all(field in userProfile for field in requiredFields)
    
    def getAudioFilePath(self, userId: str) -> Optional[str]:
        userProfile = self.getUserProfile(userId)
        if userProfile:
            return userProfile.get("audioFile")
        return None
    
    def getOutputPrefix(self, userId: str) -> str:
        userProfile = self.getUserProfile(userId)
        if userProfile:
            return userProfile.get("outputPrefix", f"{userId}Generated")
        return f"{userId}Generated"
    
    def getDefaultAudioFile(self) -> str:
        defaultConfig = self.loadDefaultConfig()
        return defaultConfig.get("defaultAudioFile", "audio_files/Palki.wav")
    
    def getDefaultOutputPrefix(self) -> str:
        defaultConfig = self.loadDefaultConfig()
        return defaultConfig.get("defaultOutputPrefix", "defaultGenerated")
    
    def getAudioFilePathWithFallback(self, userId: str) -> str:
        userAudioFile = self.getAudioFilePath(userId)
        if userAudioFile:
            return userAudioFile
        return self.getDefaultAudioFile()
    
    def getOutputPrefixWithFallback(self, userId: str) -> str:
        userProfile = self.getUserProfile(userId)
        if userProfile and "outputPrefix" in userProfile:
            return userProfile["outputPrefix"]
        return self.getDefaultOutputPrefix() 