#!/usr/bin/env python3
"""
Utility classes for F5-TTS Selenium Automation
Includes AudioFileManager and LogManager with camelCase naming
"""

import os
import shutil
import logging
from datetime import datetime
from typing import Optional, List


class AudioFileManager:
    """Manages audio files with camelCase naming conventions"""
    
    def __init__(self, audioFilesDir: str = "audio_files"):
        """
        Initialize the audio file manager
        
        Args:
            audioFilesDir: Directory containing audio files
        """
        self.audioFilesDir = audioFilesDir
        self.generatedDir = os.path.join(audioFilesDir, "generated")
        self._ensureDirectoriesExist()
    
    def _ensureDirectoriesExist(self):
        """Ensure required directories exist"""
        os.makedirs(self.audioFilesDir, exist_ok=True)
        os.makedirs(self.generatedDir, exist_ok=True)
    
    def validateAudioFile(self, filePath: str) -> bool:
        """
        Validate that an audio file exists and is accessible
        
        Args:
            filePath: Path to the audio file
            
        Returns:
            True if valid, False otherwise
        """
        if not os.path.exists(filePath):
            print(f"❌ Audio file not found: {filePath}")
            return False
        
        if not os.path.isfile(filePath):
            print(f"❌ Path is not a file: {filePath}")
            return False
        
        # Check file extension
        validExtensions = ['.wav', '.mp3', '.flac', '.ogg', '.m4a']
        fileExtension = os.path.splitext(filePath)[1].lower()
        
        if fileExtension not in validExtensions:
            print(f"⚠️ Unsupported audio format: {fileExtension}")
            print(f"   Supported formats: {', '.join(validExtensions)}")
            return False
        
        return True
    
    def getAbsolutePath(self, relativePath: str) -> str:
        """
        Convert relative path to absolute path
        
        Args:
            relativePath: Relative path to convert
            
        Returns:
            Absolute path
        """
        if os.path.isabs(relativePath):
            return relativePath
        return os.path.abspath(relativePath)
    
    def generateOutputFileName(self, userPrefix: str, timestamp: Optional[str] = None) -> str:
        """
        Generate output filename with timestamp
        
        Args:
            userPrefix: User-specific prefix
            timestamp: Optional timestamp string
            
        Returns:
            Generated filename
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"{userPrefix}_{timestamp}.wav"
    
    def getGeneratedFilePath(self, fileName: str) -> str:
        """
        Get full path for a generated file
        
        Args:
            fileName: Name of the generated file
            
        Returns:
            Full path to the generated file
        """
        return os.path.join(self.generatedDir, fileName)
    
    def listGeneratedFiles(self, userPrefix: Optional[str] = None) -> List[str]:
        """
        List generated audio files, optionally filtered by user prefix
        
        Args:
            userPrefix: Optional user prefix to filter by
            
        Returns:
            List of generated file names
        """
        try:
            files = os.listdir(self.generatedDir)
            audioFiles = [f for f in files if f.endswith('.wav')]
            
            if userPrefix:
                audioFiles = [f for f in audioFiles if f.startswith(userPrefix)]
            
            return sorted(audioFiles, reverse=True)  # Most recent first
            
        except Exception as e:
            print(f"❌ Error listing generated files: {e}")
            return []
    
    def cleanupOldFiles(self, maxFiles: int = 50) -> int:
        """
        Clean up old generated files, keeping only the most recent ones
        
        Args:
            maxFiles: Maximum number of files to keep
            
        Returns:
            Number of files deleted
        """
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
                except Exception as e:
                    print(f"⚠️ Could not delete {fileName}: {e}")
            
            if deletedCount > 0:
                print(f"🧹 Cleaned up {deletedCount} old audio files")
            
            return deletedCount
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            return 0
    
    def getFileSize(self, filePath: str) -> Optional[int]:
        """
        Get file size in bytes
        
        Args:
            filePath: Path to the file
            
        Returns:
            File size in bytes or None if error
        """
        try:
            return os.path.getsize(filePath)
        except Exception:
            return None
    
    def formatFileSize(self, sizeBytes: int) -> str:
        """
        Format file size in human-readable format
        
        Args:
            sizeBytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        if sizeBytes < 1024:
            return f"{sizeBytes} B"
        elif sizeBytes < 1024 * 1024:
            return f"{sizeBytes / 1024:.1f} KB"
        else:
            return f"{sizeBytes / (1024 * 1024):.1f} MB"


class LogManager:
    """Manages logging with camelCase naming conventions"""
    
    def __init__(self, logsDir: str = "logs", logLevel: int = logging.INFO):
        """
        Initialize the log manager
        
        Args:
            logsDir: Directory for log files
            logLevel: Logging level
        """
        self.logsDir = logsDir
        self.logLevel = logLevel
        self._ensureLogDirectoryExists()
        self._setupLogger()
    
    def _ensureLogDirectoryExists(self):
        """Ensure log directory exists"""
        os.makedirs(self.logsDir, exist_ok=True)
    
    def _setupLogger(self):
        """Setup the logger with file and console handlers"""
        # Create logger
        self.logger = logging.getLogger('F5TtsAutomation')
        self.logger.setLevel(self.logLevel)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create formatters
        fileFormatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        consoleFormatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        
        # File handler
        logFileName = f"f5tts_automation_{datetime.now().strftime('%Y%m%d')}.log"
        logFilePath = os.path.join(self.logsDir, logFileName)
        
        fileHandler = logging.FileHandler(logFilePath, encoding='utf-8')
        fileHandler.setLevel(self.logLevel)
        fileHandler.setFormatter(fileFormatter)
        
        # Console handler
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logging.WARNING)  # Only warnings and errors to console
        consoleHandler.setFormatter(consoleFormatter)
        
        # Add handlers to logger
        self.logger.addHandler(fileHandler)
        self.logger.addHandler(consoleHandler)
    
    def logInfo(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def logWarning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def logError(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def logDebug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def logUserAction(self, userId: str, action: str, details: str = ""):
        """
        Log user-specific action
        
        Args:
            userId: User ID
            action: Action performed
            details: Additional details
        """
        message = f"User: {userId} | Action: {action}"
        if details:
            message += f" | Details: {details}"
        self.logInfo(message)
    
    def logAudioGeneration(self, userId: str, textLength: int, audioFile: str, 
                          generatedFile: str, duration: float):
        """
        Log audio generation details
        
        Args:
            userId: User ID
            textLength: Length of input text
            audioFile: Reference audio file
            generatedFile: Generated audio file
            duration: Generation duration in seconds
        """
        message = (f"Audio Generated | User: {userId} | Text Length: {textLength} chars | "
                  f"Reference: {audioFile} | Output: {generatedFile} | "
                  f"Duration: {duration:.2f}s")
        self.logInfo(message)
    
    def logError(self, error: Exception, context: str = ""):
        """
        Log error with context
        
        Args:
            error: Exception object
            context: Additional context
        """
        message = f"Error: {str(error)}"
        if context:
            message = f"{context} | {message}"
        self.logger.error(message, exc_info=True)
    
    def getLogFilePath(self) -> str:
        """Get current log file path"""
        logFileName = f"f5tts_automation_{datetime.now().strftime('%Y%m%d')}.log"
        return os.path.join(self.logsDir, logFileName)
    
    def cleanupOldLogs(self, maxDays: int = 30) -> int:
        """
        Clean up log files older than specified days
        
        Args:
            maxDays: Maximum age of log files in days
            
        Returns:
            Number of files deleted
        """
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
                        except Exception as e:
                            self.logWarning(f"Could not delete old log file {fileName}: {e}")
            
            if deletedCount > 0:
                self.logInfo(f"Cleaned up {deletedCount} old log files")
            
            return deletedCount
            
        except Exception as e:
            self.logError(e, "Error during log cleanup")
            return 0 