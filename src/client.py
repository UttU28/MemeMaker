#!/usr/bin/env python3
"""
F5-TTS Gradio API Client with camelCase naming conventions
Enhanced version with user profile support using Gradio API calls
"""

import os
import time
from datetime import datetime
from typing import Optional, Dict, Any
from gradio_client import Client, handle_file

from .config import ConfigManager
from .utils import AudioFileManager, LogManager


class F5TtsGradioClient:
    
    def __init__(self, url: str = "http://localhost:7860"):
        self.url = url
        self.client = None
        self.configManager = ConfigManager()
        self.audioManager = AudioFileManager()
        self.logManager = LogManager()
        
    def connectToGradio(self) -> bool:
        try:
            self.client = Client(self.url)
            self.logManager.logInfo(f"Connected to Gradio API: {self.url}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Gradio API: {e}")
            self.logManager.logError(e, "Gradio API connection")
            return False
    
    def generateSpeechWithApi(self, audioFilePath: str, textToGenerate: str, 
                             userConfig: Optional[Dict[str, Any]] = None):
        if not self.client:
            print("❌ Not connected to Gradio API")
            return None
        
        try:
            if userConfig is None:
                userConfig = {
                    "speed": 1.0,
                    "nfeSteps": 32,
                    "crossFadeDuration": 0.15,
                    "removeSilences": False
                }
            
            if not self.audioManager.validateAudioFile(audioFilePath):
                return None
            
            absolutePath = self.audioManager.getAbsolutePath(audioFilePath)
            
            startTime = time.time()
            result = self.client.predict(
                ref_audio_input=handle_file(absolutePath),
                ref_text_input="",
                gen_text_input=textToGenerate,
                remove_silence=userConfig.get("removeSilences", False),
                randomize_seed=True,
                seed_input=0,
                cross_fade_duration_slider=userConfig.get("crossFadeDuration", 0.15),
                nfe_slider=int(userConfig.get("nfeSteps", 32)),
                speed_slider=userConfig.get("speed", 1.0),
                api_name="/basic_tts"
            )
            
            duration = time.time() - startTime
            self.logManager.logInfo(f"Speech generated via API in {duration:.2f}s: {len(textToGenerate)} chars")
            
            return result
            
        except Exception as e:
            print(f"❌ Failed to generate speech: {e}")
            self.logManager.logError(e, "Speech generation via API")
            return None
    
    def downloadAndSaveAudio(self, apiResult, outputPrefix: str) -> Optional[str]:
        try:
            if not apiResult:
                print("❌ No API result to download")
                return None
            
            # Extract audio file path from API result tuple
            if isinstance(apiResult, tuple) and len(apiResult) > 0:
                audioFilePath = apiResult[0]  # First element is the audio file path
            else:
                audioFilePath = apiResult
            
            fileName = self.audioManager.generateOutputFileName(outputPrefix)
            outputPath = self.audioManager.getGeneratedFilePath(fileName)
            
            import shutil
            shutil.copy2(audioFilePath, outputPath)
            
            fileSize = self.audioManager.getFileSize(outputPath)
            if fileSize:
                sizeStr = self.audioManager.formatFileSize(fileSize)
                self.logManager.logInfo(f"Audio saved: {fileName} ({sizeStr})")
            
            return outputPath
            
        except Exception as e:
            print(f"❌ Failed to save audio: {e}")
            self.logManager.logError(e, "Saving generated audio")
            return None
    
    def generateSpeechWithUser(self, userId: str, customText: Optional[str] = None) -> bool:
        userProfile = self.configManager.getUserProfile(userId)
        if not userProfile:
            print(f"❌ User profile not found: {userId}")
            return False
        
        userConfig = self.configManager.getUserConfig(userId)
        audioFilePath = self.configManager.getAudioFilePathWithFallback(userId)
        outputPrefix = self.configManager.getOutputPrefixWithFallback(userId)
        
        self.logManager.logUserAction(userId, "SpeechGenerationStarted", f"Audio: {audioFilePath}")
        
        startTime = time.time()
        
        try:
            if not self.client and not self.connectToGradio():
                return False
            
            if customText:
                textToGenerate = customText
            else:
                textToGenerate = "Hello, this is a test of the F5-TTS voice cloning system. The quick brown fox jumps over the lazy dog."
            
            apiResult = self.generateSpeechWithApi(audioFilePath, textToGenerate, userConfig)
            if not apiResult:
                print("❌ Failed to generate speech")
                return False
            
            savedPath = self.downloadAndSaveAudio(apiResult, outputPrefix)
            if not savedPath:
                print("❌ Failed to save generated audio")
                return False
            
            duration = time.time() - startTime
            self.logManager.logAudioGeneration(
                userId, len(textToGenerate), audioFilePath, 
                os.path.basename(savedPath), duration
            )
            
            self.logManager.logUserAction(userId, "SpeechGenerationCompleted", f"Duration: {duration:.2f}s")
            
            self.configManager.updateLastUsed(userId)
            
            return True
            
        except Exception as e:
            print(f"❌ Error during speech generation workflow: {e}")
            self.logManager.logError(e, f"Speech generation workflow for user {userId}")
            return False
    
    def generateSpeechLegacy(self, customText: Optional[str] = None) -> bool:
        defaultUserId = self.configManager.getDefaultUserId()
        return self.generateSpeechWithUser(defaultUserId, customText)
    
    def listAvailableUsers(self) -> list:
        return self.configManager.getAllUserIds()
    
    def getUserInfo(self, userId: str) -> Optional[Dict[str, Any]]:
        return self.configManager.getUserProfile(userId)
    
    def testConnection(self) -> bool:
        try:
            if not self.client:
                return self.connectToGradio()
            
            return True
            
        except Exception as e:
            print(f"❌ Gradio API connection test failed: {e}")
            self.logManager.logError(e, "API connection test")
            return False
    
    def close(self):
        if self.client:
            self.client = None
            self.logManager.logInfo("Gradio API connection closed")


# Backward compatibility alias
F5TtsSeleniumClient = F5TtsGradioClient 