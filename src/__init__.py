#!/usr/bin/env python3
"""
F5-TTS Gradio API Automation Package
A Python package for automating F5-TTS voice cloning using Gradio API calls
"""

__version__ = "2.0.0"
__author__ = "F5-TTS Automation Team"
__description__ = "F5-TTS voice cloning automation using Gradio API"

from src.client import F5TtsGradioClient
from src.config import ConfigManager
from src.utils import AudioFileManager, LogManager
from src.llm import LlmService

__all__ = [
    "F5TtsGradioClient",
    "ConfigManager",
    "AudioFileManager", 
    "LogManager",
    "LlmService"
] 