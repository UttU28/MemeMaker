#!/usr/bin/env python3
"""
Configuration Manager for F5-TTS Selenium Automation
Handles loading and managing user profiles and default configurations
"""

import json
import os
from typing import Dict, Any, Optional
from datetime import datetime


class ConfigManager:
    """Manages configuration files and user profiles with camelCase naming"""
    
    def __init__(self, profilesDir: str = "profiles"):
        """
        Initialize the configuration manager
        
        Args:
            profilesDir: Directory containing configuration files
        """
        self.profilesDir = profilesDir
        self.defaultConfigPath = os.path.join(profilesDir, "defaultConfig.json")
        self.userProfilesPath = os.path.join(profilesDir, "userProfiles.json")
        self._defaultConfig = None
        self._userProfiles = None
    
    def loadDefaultConfig(self) -> Dict[str, Any]:
        """Load the default configuration"""
        if self._defaultConfig is None:
            try:
                with open(self.defaultConfigPath, 'r', encoding='utf-8') as file:
                    self._defaultConfig = json.load(file)
            except FileNotFoundError:
                print(f"❌ Default config file not found: {self.defaultConfigPath}")
                self._defaultConfig = self._getDefaultConfigFallback()
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing default config: {e}")
                self._defaultConfig = self._getDefaultConfigFallback()
        
        return self._defaultConfig.copy()
    
    def loadUserProfiles(self) -> Dict[str, Any]:
        """Load all user profiles"""
        if self._userProfiles is None:
            try:
                with open(self.userProfilesPath, 'r', encoding='utf-8') as file:
                    self._userProfiles = json.load(file)
            except FileNotFoundError:
                print(f"❌ User profiles file not found: {self.userProfilesPath}")
                self._userProfiles = {"users": {}}
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing user profiles: {e}")
                self._userProfiles = {"users": {}}
        
        return self._userProfiles.copy()
    
    def getUserProfile(self, userId: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific user profile
        
        Args:
            userId: The user ID to retrieve
            
        Returns:
            User profile dictionary or None if not found
        """
        profiles = self.loadUserProfiles()
        return profiles.get("users", {}).get(userId)
    
    def getUserConfig(self, userId: str) -> Dict[str, Any]:
        """
        Get merged configuration for a user (default + user overrides)
        
        Args:
            userId: The user ID
            
        Returns:
            Merged configuration dictionary
        """
        defaultConfig = self.loadDefaultConfig()
        userProfile = self.getUserProfile(userId)
        
        if userProfile and "config" in userProfile:
            # Merge user config with default config
            mergedConfig = defaultConfig.copy()
            mergedConfig.update(userProfile["config"])
            return mergedConfig
        
        return defaultConfig
    
    def getAllUserIds(self) -> list:
        """Get list of all user IDs"""
        profiles = self.loadUserProfiles()
        return list(profiles.get("users", {}).keys())
    
    def updateLastUsed(self, userId: str) -> bool:
        """
        Update the last used user in the profiles file
        
        Args:
            userId: The user ID that was last used
            
        Returns:
            True if successful, False otherwise
        """
        try:
            profiles = self.loadUserProfiles()
            profiles["lastUsed"] = userId
            profiles["updatedAt"] = datetime.now().isoformat()
            
            with open(self.userProfilesPath, 'w', encoding='utf-8') as file:
                json.dump(profiles, file, indent=4, ensure_ascii=False)
            
            # Update cached version
            self._userProfiles = profiles
            return True
            
        except Exception as e:
            print(f"❌ Error updating last used user: {e}")
            return False
    
    def getDefaultUserId(self) -> str:
        """Get the default user ID"""
        profiles = self.loadUserProfiles()
        return profiles.get("defaultUser", "user1")
    
    def getLastUsedUserId(self) -> str:
        """Get the last used user ID"""
        profiles = self.loadUserProfiles()
        return profiles.get("lastUsed", self.getDefaultUserId())
    
    def _getDefaultConfigFallback(self) -> Dict[str, Any]:
        """Fallback default configuration if file is missing"""
        return {
            "speed": 0.8,
            "nfeSteps": 34,
            "crossFadeDuration": 0.16,
            "removeSilences": True,
            "f5ttsUrl": "http://localhost:7860",
            "timeoutSeconds": 300,
            "downloadDirectory": "audio_files/generated",
            "defaultAudioFile": "audio_files/user1.wav",
            "defaultOutputPrefix": "defaultGenerated"
        }
    
    def validateUserProfile(self, userId: str) -> bool:
        """
        Validate that a user profile exists and has required fields
        
        Args:
            userId: The user ID to validate
            
        Returns:
            True if valid, False otherwise
        """
        userProfile = self.getUserProfile(userId)
        if not userProfile:
            return False
        
        requiredFields = ["userName", "audioFile", "outputPrefix"]
        return all(field in userProfile for field in requiredFields)
    
    def getAudioFilePath(self, userId: str) -> Optional[str]:
        """
        Get the audio file path for a user
        
        Args:
            userId: The user ID
            
        Returns:
            Audio file path or None if not found
        """
        userProfile = self.getUserProfile(userId)
        if userProfile:
            return userProfile.get("audioFile")
        return None
    
    def getOutputPrefix(self, userId: str) -> str:
        """
        Get the output prefix for a user
        
        Args:
            userId: The user ID
            
        Returns:
            Output prefix string
        """
        userProfile = self.getUserProfile(userId)
        if userProfile:
            return userProfile.get("outputPrefix", f"{userId}Generated")
        return f"{userId}Generated"
    
    def getDefaultAudioFile(self) -> str:
        """
        Get the default audio file path from configuration
        
        Returns:
            Default audio file path
        """
        defaultConfig = self.loadDefaultConfig()
        return defaultConfig.get("defaultAudioFile", "audio_files/user1.wav")
    
    def getDefaultOutputPrefix(self) -> str:
        """
        Get the default output prefix from configuration
        
        Returns:
            Default output prefix
        """
        defaultConfig = self.loadDefaultConfig()
        return defaultConfig.get("defaultOutputPrefix", "defaultGenerated")
    
    def getAudioFilePathWithFallback(self, userId: str) -> str:
        """
        Get audio file path for user with fallback to default
        
        Args:
            userId: The user ID
            
        Returns:
            Audio file path (user-specific or default)
        """
        userAudioFile = self.getAudioFilePath(userId)
        if userAudioFile:
            return userAudioFile
        return self.getDefaultAudioFile()
    
    def getOutputPrefixWithFallback(self, userId: str) -> str:
        """
        Get output prefix for user with fallback to default
        
        Args:
            userId: The user ID
            
        Returns:
            Output prefix (user-specific or default)
        """
        userProfile = self.getUserProfile(userId)
        if userProfile and "outputPrefix" in userProfile:
            return userProfile["outputPrefix"]
        return self.getDefaultOutputPrefix() 