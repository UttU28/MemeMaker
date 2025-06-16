#!/usr/bin/env python3
"""
Utility classes for F5-TTS Gradio API Automation
Includes AudioFileManager and LogManager with camelCase naming
"""

import os
import shutil
import logging
from datetime import datetime
from typing import Optional, List


class AudioFileManager:
    
    def __init__(self, audioFilesDir: str = "data/audio_files"):
        self.audioFilesDir = audioFilesDir
        self.generatedDir = os.path.join(audioFilesDir, "generated")
        self._ensureDirectoriesExist()
    
    def _ensureDirectoriesExist(self):
        os.makedirs(self.audioFilesDir, exist_ok=True)
        os.makedirs(self.generatedDir, exist_ok=True)
    
    def validateAudioFile(self, filePath: str) -> bool:
        if not os.path.exists(filePath):
            print(f"❌ Audio file not found: {filePath}")
            return False
        
        if not os.path.isfile(filePath):
            print(f"❌ Path is not a file: {filePath}")
            return False
        
        validExtensions = ['.wav', '.mp3', '.flac', '.ogg', '.m4a']
        fileExtension = os.path.splitext(filePath)[1].lower()
        
        if fileExtension not in validExtensions:
            print(f"⚠️ Unsupported audio format: {fileExtension}")
            return False
        
        return True
    
    def getAbsolutePath(self, relativePath: str) -> str:
        if os.path.isabs(relativePath):
            return relativePath
        return os.path.abspath(relativePath)
    
    def generateOutputFileName(self, userPrefix: str, timestamp: Optional[str] = None) -> str:
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"{userPrefix}_{timestamp}.wav"
    
    def getGeneratedFilePath(self, fileName: str) -> str:
        return os.path.join(self.generatedDir, fileName)
    
    def listGeneratedFiles(self, userPrefix: Optional[str] = None) -> List[str]:
        try:
            files = os.listdir(self.generatedDir)
            audioFiles = [f for f in files if f.endswith('.wav')]
            
            if userPrefix:
                audioFiles = [f for f in audioFiles if f.startswith(userPrefix)]
            
            return sorted(audioFiles, reverse=True)
            
        except Exception as e:
            return []
    
    def cleanupOldFiles(self, maxFiles: int = 50) -> int:
        try:
            files = self.listGeneratedFiles()
            
            if len(files) <= maxFiles:
                return 0
            
            filesToDelete = files[maxFiles:]
            deletedCount = 0
            
            for fileName in filesToDelete:
                filePath = self.getGeneratedFilePath(fileName)
                try:
                    os.remove(filePath)
                    deletedCount += 1
                except Exception:
                    pass
            
            return deletedCount
            
        except Exception:
            return 0
    
    def getFileSize(self, filePath: str) -> Optional[int]:
        try:
            return os.path.getsize(filePath)
        except Exception:
            return None
    
    def formatFileSize(self, sizeBytes: int) -> str:
        if sizeBytes < 1024:
            return f"{sizeBytes} B"
        elif sizeBytes < 1024 * 1024:
            return f"{sizeBytes / 1024:.1f} KB"
        else:
            return f"{sizeBytes / (1024 * 1024):.1f} MB"


class LogManager:
    
    def __init__(self, logsDir: str = "logs", logLevel: int = logging.INFO):
        self.logsDir = logsDir
        self.logLevel = logLevel
        self._ensureLogDirectoryExists()
        self._setupLogger()
    
    def _ensureLogDirectoryExists(self):
        os.makedirs(self.logsDir, exist_ok=True)
    
    def _setupLogger(self):
        self.logger = logging.getLogger('F5TtsAutomation')
        self.logger.setLevel(self.logLevel)
        
        self.logger.handlers.clear()
        
        fileFormatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        consoleFormatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        
        logFileName = f"f5tts_automation_{datetime.now().strftime('%Y%m%d')}.log"
        logFilePath = os.path.join(self.logsDir, logFileName)
        
        fileHandler = logging.FileHandler(logFilePath, encoding='utf-8')
        fileHandler.setLevel(self.logLevel)
        fileHandler.setFormatter(fileFormatter)
        
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logging.WARNING)
        consoleHandler.setFormatter(consoleFormatter)
        
        self.logger.addHandler(fileHandler)
        self.logger.addHandler(consoleHandler)
    
    def logInfo(self, message: str):
        self.logger.info(message)
    
    def logWarning(self, message: str):
        self.logger.warning(message)
    
    def logError(self, message: str):
        self.logger.error(message)
    
    def logDebug(self, message: str):
        self.logger.debug(message)
    
    def logUserAction(self, userId: str, action: str, details: str = ""):
        message = f"User: {userId} | Action: {action}"
        if details:
            message += f" | Details: {details}"
        self.logInfo(message)
    
    def logAudioGeneration(self, userId: str, textLength: int, audioFile: str, 
                          generatedFile: str, duration: float):
        message = (f"Audio Generated | User: {userId} | Text Length: {textLength} chars | "
                  f"Reference: {audioFile} | Output: {generatedFile} | "
                  f"Duration: {duration:.2f}s")
        self.logInfo(message)
    
    def logError(self, error: Exception, context: str = ""):
        message = f"Error: {str(error)}"
        if context:
            message = f"{context} | {message}"
        self.logger.error(message, exc_info=True)
    
    def getLogFilePath(self) -> str:
        logFileName = f"f5tts_automation_{datetime.now().strftime('%Y%m%d')}.log"
        return os.path.join(self.logsDir, logFileName)
    
    def cleanupOldLogs(self, maxDays: int = 30) -> int:
        try:
            currentTime = datetime.now()
            deletedCount = 0
            
            for fileName in os.listdir(self.logsDir):
                if fileName.startswith('f5tts_automation_') and fileName.endswith('.log'):
                    filePath = os.path.join(self.logsDir, fileName)
                    fileTime = datetime.fromtimestamp(os.path.getctime(filePath))
                    
                    if (currentTime - fileTime).days > maxDays:
                        try:
                            os.remove(filePath)
                            deletedCount += 1
                        except Exception:
                            pass
            
            if deletedCount > 0:
                self.logInfo(f"Cleaned up {deletedCount} old log files")
            
            return deletedCount
            
        except Exception as e:
            self.logError(e, "Error during log cleanup")
            return 0 