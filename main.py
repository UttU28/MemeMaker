#!/usr/bin/env python3

import json
import subprocess
import os
import sys
import requests
import torch
import warnings
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import random
from pydub import AudioSegment, silence
import whisperx
import re
import glob
import logging
import traceback

from dotenv import load_dotenv
from src.client import F5TtsGradioClient
from src.config import ConfigManager
from src.utils import AudioFileManager
from src.llm import LlmService
from prompts import CHAT_GENERATION_PROMPT, GET_THE_MOOD_PROMPT

warnings.filterwarnings("ignore", category=UserWarning)
load_dotenv()

def setupLogging():
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/pipeline_errors.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

setupLogging()
logger = logging.getLogger(__name__)

class PipelineError(Exception):
    def __init__(self, stage: str, message: str, originalError: Exception = None):
        self.stage = stage
        self.message = message
        self.originalError = originalError
        super().__init__(f"[{stage}] {message}")

class UnifiedVideoPipeline:
    def __init__(self):
        self.llmService = LlmService()
        self.configManager = ConfigManager()
        self.audioManager = AudioFileManager()
        self.jsonPath = "data/wordData.json"
        self.videoOutputDir = "data/video_output"
        os.makedirs(self.videoOutputDir, exist_ok=True)
        
        self.whisperModel = None
        self.alignModel = None
        self.alignMetadata = None
        
        logger.info("🚀 Pipeline initialized and ready")
    
    def _initializeWhisperModels(self):
        """Initialize Whisper models once for better performance"""
        try:
            if self.whisperModel is None:
                logger.info("Initializing Whisper models...")
                device = "cpu"
                self.whisperModel = whisperx.load_model("base", device, compute_type="float32")
                self.alignModel, self.alignMetadata = whisperx.load_align_model(
                    language_code="en",
                    device=device,
                    model_name="WAV2VEC2_ASR_LARGE_LV60K_960H"
                )
                logger.info("✅ Whisper models initialized successfully")
        except Exception as e:
            raise PipelineError("WHISPER_INIT", f"Failed to initialize Whisper models: {str(e)}", e)
    
    def run(self, word: str, backgroundVideo: str = None):
        """Main pipeline execution with comprehensive error handling"""
        try:
            logger.info(f"🎬 Starting pipeline for: {word.upper()}")
            print(f"🎬 Starting pipeline for: {word.upper()}")
            
            # Step 0: Remove existing word data for fresh start
            logger.info("Step 0: Cleaning existing word data for fresh start...")
            self._removeExistingWordData(word)
            
            # Step 1: Check services
            logger.info("Step 1: Checking services...")
            if not self._checkServices():
                raise PipelineError("SERVICE_CHECK", "Required services are not running")
            
            # Step 2: Initialize Whisper models
            logger.info("Step 2: Initializing Whisper models...")
            self._initializeWhisperModels()
            
            # Step 3: Generate dialogue
            logger.info("Step 3: Generating dialogue...")
            dialogues = self._generateAndSaveDialogue(word)
            if not dialogues:
                raise PipelineError("DIALOGUE_GEN", "Failed to generate dialogues")
            logger.info(f"✅ Generated {len(dialogues)} dialogues")
            
            # Step 4: Generate audio files
            logger.info("Step 4: Generating audio files...")
            audioCount = self._generateAudioFiles(word, dialogues)
            if audioCount == 0:
                raise PipelineError("AUDIO_GEN", "Failed to generate any audio files")
            logger.info(f"✅ Generated {audioCount} audio files")
            
            # Step 5: Detect moods and assign images
            logger.info("Step 5: Detecting moods and assigning images...")
            self._detectMoodsAndAssignImages(word, dialogues)
            
            # Step 6: Generate final video
            logger.info("Step 6: Generating final video...")
            success = self._generateVideo(word, backgroundVideo)
            if not success:
                raise PipelineError("VIDEO_GEN", "Failed to generate final video")
            
            logger.info(f"✅ Pipeline completed successfully for '{word}'")
            print(f"✅ Pipeline completed successfully for '{word}'")
            return True
            
        except PipelineError as e:
            logger.error(f"❌ Pipeline failed at {e.stage}: {e.message}")
            if e.originalError:
                logger.error(f"Original error: {str(e.originalError)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
            print(f"❌ Pipeline failed at {e.stage}: {e.message}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error in pipeline: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            print(f"❌ Unexpected error in pipeline: {str(e)}")
            return False
    
    def _checkServices(self) -> bool:
        """Check if required services are running with detailed error reporting"""
        try:
            logger.info("Checking Gradio service at http://localhost:7860/...")
            response = requests.get("http://localhost:7860/", timeout=5)
            if response.status_code != 200:
                logger.error(f"❌ Gradio endpoint returned status code: {response.status_code}")
                print(f"❌ Gradio endpoint returned status code: {response.status_code}")
                return False
            logger.info("✅ Gradio service is running")
            return True
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ Gradio endpoint connection failed: {str(e)}")
            print(f"❌ Gradio endpoint connection failed: {str(e)}")
            return False
        except requests.exceptions.Timeout as e:
            logger.error(f"❌ Gradio endpoint timeout: {str(e)}")
            print(f"❌ Gradio endpoint timeout: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error checking Gradio service: {str(e)}")
            print(f"❌ Unexpected error checking Gradio service: {str(e)}")
            return False
    
    def _generateAndSaveDialogue(self, word: str) -> List[Tuple[str, str, str]]:
        """Generate dialogue and save to JSON with detailed error handling"""
        try:
            # Check if user profiles exist
            if not os.path.exists("data/userProfiles.json"):
                raise PipelineError("FILE_CHECK", "data/userProfiles.json not found")
            
            # Generate dialogue using LLM
            logger.info(f"Generating dialogue for word: {word}")
            prompt = CHAT_GENERATION_PROMPT.format(word=word.capitalize())
            dialogue = self.llmService.generate(prompt, provider="openai")
            
            if not dialogue:
                raise PipelineError("LLM_GEN", "LLM returned empty dialogue")
            
            dialogue = self.llmService.cleanResponse(dialogue)
            logger.info(f"Generated dialogue length: {len(dialogue)} characters")
            
            # Parse dialogue
            dialogues = []
            lines_processed = 0
            for line in dialogue.split("\n"):
                if not line.strip():
                    continue
                lines_processed += 1
                
                try:
                    if "{" not in line or "}" not in line:
                        logger.warning(f"Skipping malformed line {lines_processed}: {line}")
                        continue
                        
                    personName = line.split("}")[0].split("{")[1]
                    lineText = line.split("}")[1].strip()
                    userId = self._getUserId(personName)
                    
                    if userId:
                        dialogues.append((lineText, personName, userId))
                        logger.info(f"Added dialogue for {personName}: {lineText[:50]}...")
                    else:
                        logger.warning(f"User ID not found for person: {personName}")
                        
                except IndexError as e:
                    logger.warning(f"Failed to parse line {lines_processed}: {line} - {str(e)}")
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error parsing line {lines_processed}: {line} - {str(e)}")
                    continue
            
            if not dialogues:
                raise PipelineError("DIALOGUE_PARSE", f"No valid dialogues parsed from {lines_processed} lines")
            
            # Save to JSON
            self._initializeWordData(word)
            self._saveDialoguesToJson(word, dialogues)
            
            logger.info(f"Successfully parsed {len(dialogues)} dialogues from {lines_processed} lines")
            return dialogues
            
        except PipelineError:
            raise
        except Exception as e:
            raise PipelineError("DIALOGUE_GEN", f"Unexpected error generating dialogue: {str(e)}", e)
    
    def _generateAudioFiles(self, word: str, dialogues: List[Tuple[str, str, str]]) -> int:
        """Generate audio files for all dialogues with detailed error handling"""
        client = None
        audioCount = 0
        
        try:
            logger.info("Initializing F5TTS Gradio client...")
            client = F5TtsGradioClient()
            
            if not client.connectToGradio():
                raise PipelineError("GRADIO_CONNECT", "Failed to connect to Gradio client")
            
            logger.info("✅ Connected to Gradio client")
            
            for i, (lineText, personName, userId) in enumerate(dialogues, 1):
                try:
                    chatId = f"chat{i}"
                    logger.info(f"Generating audio for {chatId} ({personName}): {lineText[:50]}...")
                    
                    # Generate audio
                    success = client.generateSpeechWithUser(userId, lineText)
                    
                    if not success:
                        logger.error(f"❌ Failed to generate speech for {chatId}")
                        continue
                    
                    # Get generated file
                    outputPrefix = self.configManager.getOutputPrefixWithFallback(userId)
                    if not outputPrefix:
                        logger.error(f"❌ No output prefix found for user {userId}")
                        continue
                    
                    generatedFiles = self.audioManager.listGeneratedFiles(outputPrefix)
                    
                    if not generatedFiles:
                        logger.error(f"❌ No generated files found for {chatId} with prefix {outputPrefix}")
                        continue
                    
                    audioFileName = generatedFiles[0]
                    logger.info(f"Found generated file: {audioFileName}")
                    
                    # Clean audio
                    cleanedFileName = self._cleanAudioFile(audioFileName)
                    if not cleanedFileName:
                        logger.error(f"❌ Failed to clean audio file: {audioFileName}")
                        continue
                    
                    audioPath = f"audio_files/generated/{cleanedFileName}"
                    
                    # Verify cleaned file exists
                    fullPath = f"data/{audioPath}"
                    if not os.path.exists(fullPath):
                        logger.error(f"❌ Cleaned audio file not found: {fullPath}")
                        continue
                    
                    self._updateAudioInJson(word, chatId, audioPath)
                    audioCount += 1
                    logger.info(f"✅ Successfully generated audio for {chatId}")
                    
                except Exception as e:
                    logger.error(f"❌ Error generating audio for chat{i}: {str(e)}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    continue
                    
        except PipelineError:
            raise
        except Exception as e:
            raise PipelineError("AUDIO_GEN", f"Unexpected error in audio generation: {str(e)}", e)
        finally:
            if client:
                try:
                    client.close()
                    logger.info("Closed Gradio client")
                except Exception as e:
                    logger.warning(f"Error closing Gradio client: {str(e)}")
        
        return audioCount
    
    def _detectMoodsAndAssignImages(self, word: str, dialogues: List[Tuple[str, str, str]]):
        """Detect moods and assign images for dialogues with error handling"""
        try:
            # Check if Ollama is running
            if not self.llmService.isOllamaRunning():
                logger.warning("⚠️ Ollama not running, skipping mood detection")
                return
            
            # Check if user profiles exist
            if not os.path.exists("data/userProfiles.json"):
                logger.error("❌ data/userProfiles.json not found for mood detection")
                return
            
            with open("data/userProfiles.json", "r") as f:
                profiles = json.load(f)
            
            for i, (lineText, personName, userId) in enumerate(dialogues, 1):
                try:
                    chatId = f"chat{i}"
                    speaker = personName.lower()
                    
                    # Get available emotions for speaker
                    if speaker not in profiles.get("users", {}):
                        logger.warning(f"Speaker '{speaker}' not found in user profiles")
                        continue
                    
                    emotions = profiles["users"][speaker].get("emotions", {})
                    if not emotions:
                        logger.warning(f"No emotions defined for speaker '{speaker}'")
                        continue
                    
                    expressions = list(emotions.keys())
                    
                    # Detect mood
                    options = ", ".join(expressions)
                    prompt = GET_THE_MOOD_PROMPT.format(sentence=lineText, options=options)
                    
                    logger.info(f"Detecting mood for {chatId}: {lineText[:30]}...")
                    response = self.llmService.generate(prompt, provider="ollama", model="llama3.2")
                    
                    if response and response.strip().lower() in [exp.lower() for exp in expressions]:
                        mood = response.strip().lower()
                        imageFile = emotions[mood]
                        
                        # Verify image file exists
                        if os.path.exists(imageFile):
                            self._updateImageInJson(word, chatId, imageFile)
                            logger.info(f"✅ Assigned {mood} image for {chatId}: {imageFile}")
                        else:
                            logger.warning(f"⚠️ Image file not found: {imageFile}")
                    else:
                        logger.warning(f"⚠️ Invalid mood response for {chatId}: {response}")
                        
                except Exception as e:
                    logger.error(f"❌ Error processing mood for chat{i}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Error in mood detection: {str(e)}")
            # Don't raise error here as mood detection is optional
    
    def _generateVideo(self, word: str, backgroundVideo: str = None) -> bool:
        """Generate final video with subtitles and comprehensive error handling"""
        try:
            logger.info("Loading word data for video generation...")
            wordData = self._loadWordData(word)
            if not wordData:
                raise PipelineError("DATA_LOAD", f"Failed to load word data for '{word}'")
            
            # Validate and fill missing images before processing
            logger.info("Validating and filling missing images...")
            self._validateAndFillMissingImages(word, wordData)
            
            # Reload word data after potential updates
            wordData = self._loadWordData(word)
            if not wordData:
                raise PipelineError("DATA_RELOAD", f"Failed to reload word data for '{word}' after image validation")
            
            # Check background video
            if not backgroundVideo:
                backgroundVideo = r"downloads/Minecraft Parkour Gameplay No Copyright_mobile.mp4"
            
            if not os.path.exists(backgroundVideo):
                raise PipelineError("FILE_CHECK", f"Background video not found: {backgroundVideo}")
            
            logger.info(f"Using background video: {backgroundVideo}")
            
            # Create timeline
            logger.info("Creating timeline...")
            timeline, totalDuration = self._createTimeline(wordData)
            if not timeline:
                raise PipelineError("TIMELINE", "Failed to create timeline - no valid audio/subtitle segments")
            
            logger.info(f"Created timeline with {len(timeline)} segments, total duration: {totalDuration:.2f}s")
            
            # Concatenate audio
            logger.info("Concatenating audio files...")
            combinedAudioPath = f"{self.videoOutputDir}/{word}_combined_audio.wav"
            if not self._concatenateAudioFiles(timeline, combinedAudioPath):
                raise PipelineError("AUDIO_CONCAT", "Failed to concatenate audio files")
            
            # Verify concatenated audio exists
            if not os.path.exists(combinedAudioPath):
                raise PipelineError("FILE_CHECK", f"Concatenated audio file not found: {combinedAudioPath}")
            
            logger.info(f"✅ Audio concatenated: {combinedAudioPath}")
            
            # Generate final video with subtitles
            logger.info("Generating final video with FFmpeg...")
            finalVideoPath = f"{self.videoOutputDir}/{word}_final_video.mp4"
            if not self._generateBaseVideo(backgroundVideo, timeline, totalDuration, 
                                         combinedAudioPath, finalVideoPath, word):
                raise PipelineError("FFMPEG", "FFmpeg video generation failed")
            
            # Verify final video exists
            if not os.path.exists(finalVideoPath):
                raise PipelineError("FILE_CHECK", f"Final video file not created: {finalVideoPath}")
            
            logger.info(f"✅ Final video generated: {finalVideoPath}")
            
            # Update final video path in JSON
            self._updateFinalVideoInJson(word, finalVideoPath)
            
            # Cleanup temp files
            try:
                for tempFile in [combinedAudioPath]:
                    if os.path.exists(tempFile):
                        os.remove(tempFile)
                        logger.info(f"Cleaned up temp file: {tempFile}")
            except Exception as e:
                logger.warning(f"Warning: Failed to cleanup temp files: {str(e)}")
            
            return True
            
        except PipelineError:
            raise
        except Exception as e:
            raise PipelineError("VIDEO_GEN", f"Unexpected error in video generation: {str(e)}", e)
    
    def _validateAndFillMissingImages(self, word: str, wordData: Dict):
        """Validate and fill missing image files with default confident emotion images"""
        try:
            # Load user profiles
            if not os.path.exists("data/userProfiles.json"):
                logger.error("❌ data/userProfiles.json not found for image validation")
                return
                
            with open("data/userProfiles.json", "r") as f:
                profiles = json.load(f)
            
            chats = wordData.get("chats", {})
            if not chats:
                logger.warning("⚠️ No chats found in word data")
                return
                
            needsUpdate = False
            
            for chatId, chatData in chats.items():
                try:
                    speaker = chatData.get("speaker", "").lower()
                    imageFile = chatData.get("imageFile", "")
                    
                    # Check if image file is missing or doesn't exist
                    if not imageFile or not os.path.exists(imageFile):
                        print(f"🔍 Missing image for {chatId} (speaker: {speaker}), looking for default...")
                        logger.info(f"Missing image for {chatId} (speaker: {speaker}), looking for default...")
                        
                        # Find speaker in profiles
                        if speaker in profiles.get("users", {}):
                            userEmotions = profiles["users"][speaker].get("emotions", {})
                            
                            # Try to get confident emotion as default
                            if "confident" in userEmotions:
                                defaultImage = userEmotions["confident"]
                                
                                # Verify the default image exists
                                if os.path.exists(defaultImage):
                                    print(f"✅ Using default confident image for {speaker}: {defaultImage}")
                                    logger.info(f"Using default confident image for {speaker}: {defaultImage}")
                                    chatData["imageFile"] = defaultImage
                                    needsUpdate = True
                                else:
                                    print(f"⚠️ Default confident image not found for {speaker}: {defaultImage}")
                                    logger.warning(f"Default confident image not found for {speaker}: {defaultImage}")
                            else:
                                # If no confident emotion, try to get any available emotion
                                if userEmotions:
                                    firstEmotion = list(userEmotions.keys())[0]
                                    defaultImage = userEmotions[firstEmotion]
                                    
                                    if os.path.exists(defaultImage):
                                        print(f"✅ Using {firstEmotion} image for {speaker}: {defaultImage}")
                                        logger.info(f"Using {firstEmotion} image for {speaker}: {defaultImage}")
                                        chatData["imageFile"] = defaultImage
                                        needsUpdate = True
                                    else:
                                        print(f"⚠️ No valid images found for speaker: {speaker}")
                                        logger.warning(f"No valid images found for speaker: {speaker}")
                                else:
                                    print(f"⚠️ No emotions defined for speaker: {speaker}")
                                    logger.warning(f"No emotions defined for speaker: {speaker}")
                        else:
                            print(f"⚠️ Speaker '{speaker}' not found in user profiles")
                            logger.warning(f"Speaker '{speaker}' not found in user profiles")
                            
                except Exception as e:
                    logger.error(f"Error processing image for {chatId}: {str(e)}")
                    continue
            
            # Update JSON if changes were made
            if needsUpdate:
                try:
                    with open(self.jsonPath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if word.lower() in data["words"]:
                        data["words"][word.lower()]["chats"] = chats
                        
                        with open(self.jsonPath, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=4, ensure_ascii=False)
                        
                        print(f"✅ Updated {word} with default images")
                        logger.info(f"Updated {word} with default images")
                except Exception as e:
                    logger.error(f"Failed to update word data: {str(e)}")
                    raise PipelineError("JSON_UPDATE", f"Failed to update word data: {str(e)}", e)
                    
        except PipelineError:
            raise
        except Exception as e:
            logger.error(f"Error validating images: {str(e)}")
            raise PipelineError("IMAGE_VALIDATION", f"Error validating images: {str(e)}", e)
    
    def _cleanAudioFile(self, audioFileName: str) -> Optional[str]:
        """Clean audio file by trimming silence with error handling"""
        try:
            inputPath = self.audioManager.getGeneratedFilePath(audioFileName)
            
            if not os.path.exists(inputPath):
                logger.error(f"Audio file not found for cleaning: {inputPath}")
                return None
            
            logger.info(f"Cleaning audio file: {audioFileName}")
            
            audio = AudioSegment.from_file(inputPath)
            
            # Detect non-silent chunks
            chunks = silence.detect_nonsilent(
                audio,
                min_silence_len=100,
                silence_thresh=-40
            )
            
            if not chunks:
                logger.warning(f"No non-silent chunks found in audio: {audioFileName}")
                return None
            
            # Trim with padding
            paddingMs = 50
            startTrim = max(0, chunks[0][0] - paddingMs)
            endTrim = min(len(audio), chunks[-1][1] + paddingMs)
            
            cleanedAudio = audio[startTrim:endTrim]
            
            # Save cleaned file
            baseName = os.path.splitext(audioFileName)[0]
            cleanedFileName = f"trimmed_{baseName}.wav"
            outputPath = self.audioManager.getGeneratedFilePath(cleanedFileName)
            cleanedAudio.export(outputPath, format="wav")
            
            # Verify cleaned file was created
            if not os.path.exists(outputPath):
                logger.error(f"Cleaned audio file was not created: {outputPath}")
                return None
            
            logger.info(f"✅ Audio cleaned: {cleanedFileName}")
            return cleanedFileName
            
        except Exception as e:
            logger.error(f"Error cleaning audio file {audioFileName}: {str(e)}")
            return None
    
    def _generateSingleSubtitle(self, audioFile: str, dialogue: str) -> Optional[Dict]:
        """Generate subtitle information for a single audio clip with detailed error handling"""
        tempAudioPath = "temp_single_audio.wav"
        
        try:
            # Validate input parameters
            if not audioFile or not dialogue:
                logger.error("❌ Missing audioFile or dialogue for subtitle generation")
                return None
            
            # Ensure audio file path is correct
            if not audioFile.startswith('data/'):
                audioFile = 'data/' + audioFile
            
            # Check if audio file exists
            if not os.path.exists(audioFile):
                logger.error(f"❌ Audio file not found for subtitle generation: {audioFile}")
                return None
            
            logger.info(f"Generating subtitles for: {audioFile}")
            
            # Copy audio file to temp location
            try:
                audio = AudioSegment.from_file(audioFile)
                audio.export(tempAudioPath, format="wav")
                logger.info(f"✅ Audio exported to temp file: {tempAudioPath}")
            except Exception as e:
                logger.error(f"❌ Failed to load/export audio file {audioFile}: {str(e)}")
                return None
            
            # Verify Whisper models are initialized
            if not self.whisperModel or not self.alignModel:
                logger.error("❌ Whisper models not initialized for subtitle generation")
                return None
            
            # Transcribe with Whisper (using pre-loaded models)
            try:
                logger.info("Starting Whisper transcription...")
                transcription = self.whisperModel.transcribe(
                    tempAudioPath,
                    batch_size=1,
                    language="en",
                    task="transcribe"
                )
                
                if not transcription.get("segments"):
                    logger.warning("❌ No segments found in transcription")
                    return None
                
                logger.info(f"✅ Transcription completed with {len(transcription['segments'])} segments")
                
            except Exception as e:
                logger.error(f"❌ Whisper transcription failed: {str(e)}")
                return None
            
            # Align words (using pre-loaded models)
            try:
                logger.info("Starting word alignment...")
                alignedData = whisperx.align(
                    transcription["segments"],
                    self.alignModel,
                    self.alignMetadata,
                    tempAudioPath,
                    "cpu",
                    return_char_alignments=False
                )
                
                if not alignedData.get("word_segments"):
                    logger.warning("❌ No word segments found in alignment")
                    return None
                
                logger.info(f"✅ Word alignment completed with {len(alignedData['word_segments'])} word segments")
                
            except Exception as e:
                logger.error(f"❌ Word alignment failed: {str(e)}")
                return None
            
            # Parse original dialogue text into words
            try:
                originalWords = []
                cleanLine = re.sub(r'[^\w\s]', '', dialogue.strip())
                words = cleanLine.split()
                originalWords.extend(words)
                
                if not originalWords:
                    logger.warning("❌ No words found in original dialogue")
                    return None
                
                logger.info(f"Original dialogue parsed into {len(originalWords)} words")
                
            except Exception as e:
                logger.error(f"❌ Failed to parse original dialogue: {str(e)}")
                return None
            
            # Create subtitle segments
            try:
                wordSegments = alignedData["word_segments"]
                subtitleSegments = []
                groupSize = 4
                
                for i in range(0, len(wordSegments), groupSize):
                    group = wordSegments[i:i+groupSize]
                    start = group[0]['start']
                    end = group[-1]['end']
                    
                    # Use original words instead of Whisper transcribed words
                    groupWords = []
                    for j, segment in enumerate(group):
                        originalIndex = i + j
                        if originalIndex < len(originalWords):
                            groupWords.append(originalWords[originalIndex])
                        else:
                            groupWords.append(segment['word'].strip())
                    
                    text = " ".join([w for w in groupWords if w])
                    if text:  # Only add non-empty segments
                        subtitleSegments.append({
                            "start": start,
                            "end": end,
                            "text": text
                        })
                
                if not subtitleSegments:
                    logger.warning("❌ No subtitle segments created")
                    return None
                
                logger.info(f"✅ Created {len(subtitleSegments)} subtitle segments")
                
                return {
                    "segments": subtitleSegments,
                    "duration": len(audio) / 1000.0  # Convert to seconds
                }
                
            except Exception as e:
                logger.error(f"❌ Failed to create subtitle segments: {str(e)}")
                return None
            
        except Exception as e:
            logger.error(f"❌ Unexpected error generating subtitle: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
        finally:
            # Cleanup temp file
            try:
                if os.path.exists(tempAudioPath):
                    os.remove(tempAudioPath)
                    logger.info(f"Cleaned up temp file: {tempAudioPath}")
            except Exception as e:
                logger.warning(f"Warning: Failed to cleanup temp file {tempAudioPath}: {str(e)}")

    def _createTimeline(self, wordData: Dict) -> Tuple[List[Dict], float]:
        """Create timeline for video generation with comprehensive error handling"""
        try:
            # Validate input data
            if not wordData:
                logger.error("❌ No word data provided for timeline creation")
                return [], 0
            
            chats = wordData.get("chats", {})
            if not chats:
                logger.error("❌ No chats found in word data for timeline creation")
                return [], 0
            
            timeline = []
            currentTime = 0
            skipped_count = 0
            
            logger.info(f"Creating timeline from {len(chats)} chats...")
            
            for chatId in sorted(chats.keys(), key=lambda x: int(x.replace('chat', ''))):
                try:
                    chatData = chats[chatId]
                    audioFile = chatData.get("audioFile", "")
                    dialogue = chatData.get("dialogue", "")
                    speaker = chatData.get("speaker", "")
                    
                    # Validate chat data
                    if not audioFile:
                        logger.warning(f"⚠️ No audio file for {chatId}, skipping...")
                        skipped_count += 1
                        continue
                    
                    if not dialogue:
                        logger.warning(f"⚠️ No dialogue for {chatId}, skipping...")
                        skipped_count += 1
                        continue
                    
                    # Check if audio file exists
                    full_audio_path = audioFile if audioFile.startswith('data/') else f'data/{audioFile}'
                    if not os.path.exists(full_audio_path):
                        logger.error(f"❌ Audio file not found for {chatId}: {full_audio_path}")
                        skipped_count += 1
                        continue
                    
                    logger.info(f"Processing {chatId}: {dialogue[:30]}...")
                    
                    # Generate subtitle information for this clip
                    subtitleInfo = self._generateSingleSubtitle(audioFile, dialogue)
                    if not subtitleInfo:
                        logger.error(f"❌ Failed to generate subtitle info for {chatId}")
                        skipped_count += 1
                        continue
                    
                    timeline_item = {
                        "chatId": chatId,
                        "speaker": speaker,
                        "dialogue": dialogue,
                        "audioFile": audioFile,
                        "imageFile": chatData.get("imageFile", ""),
                        "startTime": currentTime,
                        "endTime": currentTime + subtitleInfo["duration"],
                        "duration": subtitleInfo["duration"],
                        "subtitleSegments": subtitleInfo["segments"]
                    }
                    
                    timeline.append(timeline_item)
                    currentTime += subtitleInfo["duration"]
                    
                    logger.info(f"✅ Added {chatId} to timeline (duration: {subtitleInfo['duration']:.2f}s)")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing {chatId}: {str(e)}")
                    skipped_count += 1
                    continue
            
            if not timeline:
                logger.error("❌ No valid timeline items created")
                return [], 0
            
            logger.info(f"✅ Timeline created with {len(timeline)} items (skipped {skipped_count}), total duration: {currentTime:.2f}s")
            return timeline, currentTime
            
        except Exception as e:
            logger.error(f"❌ Unexpected error creating timeline: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return [], 0
    
    def _concatenateAudioFiles(self, timeline: List[Dict], outputPath: str) -> bool:
        """Concatenate audio files with comprehensive error handling"""
        try:
            # Validate inputs
            if not timeline:
                logger.error("❌ No timeline provided for audio concatenation")
                return False
            
            if not outputPath:
                logger.error("❌ No output path provided for audio concatenation")
                return False
            
            logger.info(f"Concatenating {len(timeline)} audio files...")
            
            combinedAudio = AudioSegment.empty()
            processed_count = 0
            
            for i, item in enumerate(timeline):
                try:
                    audioFile = item.get("audioFile", "")
                    if not audioFile:
                        logger.warning(f"⚠️ No audio file in timeline item {i}, skipping...")
                        continue
                    
                    # Ensure proper path
                    if not audioFile.startswith('data/'):
                        audioFile = 'data/' + audioFile
                    
                    # Check if file exists
                    if not os.path.exists(audioFile):
                        logger.error(f"❌ Audio file not found: {audioFile}")
                        continue
                    
                    logger.info(f"Loading audio file {i+1}/{len(timeline)}: {audioFile}")
                    
                    # Load and add audio
                    audio = AudioSegment.from_file(audioFile)
                    
                    # Validate audio duration
                    if len(audio) == 0:
                        logger.warning(f"⚠️ Audio file has zero duration: {audioFile}")
                        continue
                    
                    combinedAudio += audio
                    processed_count += 1
                    
                    logger.info(f"✅ Added audio {i+1}: {len(audio)/1000:.2f}s")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing audio file {i}: {str(e)}")
                    continue
            
            if processed_count == 0:
                logger.error("❌ No audio files were successfully processed")
                return False
            
            # Export combined audio
            try:
                logger.info(f"Exporting combined audio to: {outputPath}")
                
                # Ensure output directory exists
                os.makedirs(os.path.dirname(outputPath), exist_ok=True)
                
                combinedAudio.export(outputPath, format="wav")
                
                # Verify exported file
                if not os.path.exists(outputPath):
                    logger.error(f"❌ Combined audio file was not created: {outputPath}")
                    return False
                
                # Check file size
                file_size = os.path.getsize(outputPath)
                if file_size == 0:
                    logger.error(f"❌ Combined audio file is empty: {outputPath}")
                    return False
                
                logger.info(f"✅ Audio concatenation successful: {processed_count} files, duration: {len(combinedAudio)/1000:.2f}s, size: {file_size} bytes")
                return True
                
            except Exception as e:
                logger.error(f"❌ Failed to export combined audio: {str(e)}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Unexpected error in audio concatenation: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def _generateBaseVideo(self, backgroundVideo: str, timeline: List[Dict], 
                          totalDuration: float, combinedAudio: str, outputVideo: str, word: str) -> bool:
        """Generate base video with FFmpeg and comprehensive error handling"""
        try:
            # Validate inputs
            if not backgroundVideo or not os.path.exists(backgroundVideo):
                logger.error(f"❌ Background video not found: {backgroundVideo}")
                return False
            
            if not timeline:
                logger.error("❌ No timeline provided for video generation")
                return False
            
            if not combinedAudio or not os.path.exists(combinedAudio):
                logger.error(f"❌ Combined audio file not found: {combinedAudio}")
                return False
            
            if totalDuration <= 0:
                logger.error(f"❌ Invalid total duration: {totalDuration}")
                return False
            
            if not outputVideo:
                logger.error("❌ No output video path provided")
                return False
            
            logger.info(f"Generating video with FFmpeg...")
            logger.info(f"Background: {backgroundVideo}")
            logger.info(f"Audio: {combinedAudio}")
            logger.info(f"Duration: {totalDuration:.2f}s")
            logger.info(f"Output: {outputVideo}")
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(outputVideo), exist_ok=True)
            
            # Check for outro
            outroPath = "data/outro.mp4"
            useOutro = os.path.exists(outroPath)
            if useOutro:
                logger.info(f"✅ Using outro video: {outroPath}")
            else:
                logger.info("ℹ️ No outro video found, proceeding without outro")
            
            # Check font file
            fontPath = 'C:/Windows/Fonts/impact.ttf'
            if not os.path.exists(fontPath):
                logger.warning(f"⚠️ Font file not found: {fontPath}, using default font")
                fontPath = 'arial'  # Fallback to system default
            else:
                # Escape colons in Windows paths for FFmpeg
                fontPath = fontPath.replace(':', '\\:')
            
            # Build FFmpeg command
            filterParts = []
            inputParts = ['-hwaccel', 'cuda', '-stream_loop', '-1', '-i', backgroundVideo, '-i', combinedAudio]
            
            if useOutro:
                inputParts.extend(['-i', outroPath])
                inputIndex = 3
            else:
                inputIndex = 2
            
            # Add image inputs and validate them
            imageInputs = {}
            valid_images = 0
            for item in timeline:
                imageFile = item.get("imageFile", "")
                if imageFile and os.path.exists(imageFile):
                    inputParts.extend(['-i', imageFile])
                    imageInputs[item["chatId"]] = inputIndex
                    inputIndex += 1
                    valid_images += 1
                    logger.info(f"✅ Added image for {item['chatId']}: {imageFile}")
                else:
                    logger.warning(f"⚠️ No valid image for {item['chatId']}: {imageFile}")
            
            logger.info(f"Added {valid_images} valid images out of {len(timeline)} timeline items")
            
            # Build filter complex with error checking
            try:
                # Background video processing
                filterParts.append(f"[0:v]scale=1080:1920:force_original_aspect_ratio=disable,setsar=1,trim=duration={totalDuration},setpts=PTS-STARTPTS[bg]")
                currentBase = "[bg]"
                
                # Add overlays and subtitles
                overlay_count = 0
                subtitle_count = 0
                
                for i, item in enumerate(timeline):
                    chatId = item.get("chatId", f"chat{i}")
                    
                    # Add image overlay if available
                    if chatId in imageInputs:
                        imgInput = imageInputs[chatId]
                        filterParts.append(
                            f"{currentBase}[{imgInput}:v]overlay=0:0:enable='between(t,{item['startTime']},{item['endTime']})'[overlay{overlay_count}]"
                        )
                        currentBase = f"[overlay{overlay_count}]"
                        overlay_count += 1
                    
                    # Add subtitles for this segment
                    if "subtitleSegments" in item and item["subtitleSegments"]:
                        for j, segment in enumerate(item["subtitleSegments"]):
                            start = item["startTime"] + segment["start"]
                            end = item["startTime"] + segment["end"]
                            text = segment.get("text", "").strip()
                            
                            if not text:
                                continue
                                
                            # Escape special characters in text for FFmpeg
                            text = text.replace("'", "\\'").replace('"', '\\"').replace(':', '\\:')
                            
                            filterParts.append(
                                f"{currentBase}drawtext=text='{text}':fontfile='{fontPath}':fontsize=64:borderw=3:bordercolor=black:fontcolor=white:x=(w-text_w)/2:y=h-th-150:enable='between(t,{start:.3f},{end:.3f})'[sub{subtitle_count}]"
                            )
                            currentBase = f"[sub{subtitle_count}]"
                            subtitle_count += 1
                
                logger.info(f"Added {overlay_count} overlays and {subtitle_count} subtitle segments")
                
                # Add main title overlays
                mainWord = word.upper().replace("'", "\\'").replace('"', '\\"')
                
                # Add "Today's Word!" title
                filterParts.append(
                    f"{currentBase}drawtext=text='Todays Word!':fontfile='{fontPath}':fontsize=60:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=80[title]"
                )
                
                # Add the main word
                filterParts.append(
                    f"[title]drawtext=text='{mainWord}':fontfile='{fontPath}':fontsize=140:fontcolor=yellow:borderw=6:bordercolor=black:x=(w-text_w)/2:y=140[word_overlay]"
                )
                currentBase = "[word_overlay]"
                
                # Add outro if exists
                if useOutro:
                    try:
                        outroDuration = self._getVideoDuration(outroPath)
                        logger.info(f"Outro duration: {outroDuration:.2f}s")
                        
                        filterParts.append(f"[2:v]scale=1080:1920:force_original_aspect_ratio=disable,setsar=1[outro_scaled]")
                        filterParts.append(f"{currentBase}[outro_scaled]concat=n=2:v=1:a=0[final_video]")
                        
                        # Handle audio
                        filterParts.append(f"anullsrc=channel_layout=mono:sample_rate=24000[silence]")
                        filterParts.append(f"[1:a][silence]concat=n=2:v=0:a=1[temp_audio]")
                        filterParts.append(f"[temp_audio]atrim=duration={totalDuration + outroDuration}[final_audio]")
                        outputMapping = ['-map', '[final_video]', '-map', '[final_audio]']
                    except Exception as e:
                        logger.warning(f"⚠️ Error processing outro, proceeding without: {str(e)}")
                        useOutro = False
                
                if not useOutro:
                    filterParts.append(f"{currentBase}setpts=PTS-STARTPTS[final_video]")
                    outputMapping = ['-map', '[final_video]', '-map', '1:a']
                
            except Exception as e:
                logger.error(f"❌ Error building FFmpeg filters: {str(e)}")
                return False
            
            # Build final FFmpeg command
            try:
                filterComplex = ";".join(filterParts)
                
                # Log filter complex for debugging (truncated)
                if len(filterComplex) > 500:
                    logger.info(f"Filter complex (first 500 chars): {filterComplex[:500]}...")
                else:
                    logger.info(f"Filter complex: {filterComplex}")
                
                cmd = [
                    'ffmpeg', '-y',
                    *inputParts,
                    '-filter_complex', filterComplex,
                    *outputMapping,
                    '-c:v', 'h264_nvenc',
                    '-preset', 'fast',
                    '-c:a', 'aac',
                    '-shortest',
                    outputVideo
                ]
                
                logger.info("Executing FFmpeg command...")
                logger.info(f"FFmpeg inputs: {len(inputParts)//2 - 1} files")
                
            except Exception as e:
                logger.error(f"❌ Error building FFmpeg command: {str(e)}")
                return False
            
            # Execute FFmpeg with detailed error handling
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 minute timeout
                
                if result.returncode != 0:
                    logger.error(f"❌ FFmpeg failed with return code: {result.returncode}")
                    logger.error(f"FFmpeg stderr: {result.stderr}")
                    logger.error(f"FFmpeg stdout: {result.stdout}")
                    return False
                
                # Verify output file was created
                if not os.path.exists(outputVideo):
                    logger.error(f"❌ Output video file was not created: {outputVideo}")
                    return False
                
                # Check file size
                file_size = os.path.getsize(outputVideo)
                if file_size == 0:
                    logger.error(f"❌ Output video file is empty: {outputVideo}")
                    return False
                
                logger.info(f"✅ FFmpeg video generation successful!")
                logger.info(f"Output file: {outputVideo}")
                logger.info(f"File size: {file_size} bytes")
                
                # Log any warnings from FFmpeg
                if result.stderr and "warning" in result.stderr.lower():
                    logger.warning(f"FFmpeg warnings: {result.stderr}")
                
                return True
                
            except subprocess.TimeoutExpired:
                logger.error("❌ FFmpeg process timed out (5 minutes)")
                return False
            except Exception as e:
                logger.error(f"❌ Error executing FFmpeg: {str(e)}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Unexpected error in video generation: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    # Helper methods
    def _getUserId(self, personName: str) -> Optional[str]:
        """Get user ID from person name"""
        with open("data/userProfiles.json", "r") as f:
            data = json.load(f)
            for userId, userData in data["users"].items():
                if userData["displayName"].lower() == personName.lower():
                    return userId
        return None
    
    def _initializeWordData(self, word: str):
        """Initialize word data in JSON with error handling"""
        try:
            if os.path.exists(self.jsonPath):
                with open(self.jsonPath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"Loaded existing word data from {self.jsonPath}")
            else:
                data = {"words": {}}
                logger.info(f"Creating new word data file: {self.jsonPath}")
            
            data["words"][word.lower()] = {
                "word": word.lower(),
                "chats": {}
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.jsonPath), exist_ok=True)
            
            with open(self.jsonPath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            logger.info(f"✅ Initialized word data for '{word}'")
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error in word data file: {str(e)}")
            raise PipelineError("JSON_PARSE", f"Failed to parse word data JSON: {str(e)}", e)
        except Exception as e:
            logger.error(f"❌ Error initializing word data: {str(e)}")
            raise PipelineError("JSON_INIT", f"Failed to initialize word data: {str(e)}", e)
    
    def _saveDialoguesToJson(self, word: str, dialogues: List[Tuple[str, str, str]]):
        """Save dialogues to JSON with error handling"""
        try:
            if not os.path.exists(self.jsonPath):
                logger.error(f"❌ Word data file not found: {self.jsonPath}")
                raise PipelineError("FILE_CHECK", f"Word data file not found: {self.jsonPath}")
            
            with open(self.jsonPath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if "words" not in data:
                data["words"] = {}
            
            chats = {}
            for i, (lineText, personName, userId) in enumerate(dialogues, 1):
                chats[f"chat{i}"] = {
                    "dialogue": lineText,
                    "speaker": personName.lower()
                }
            
            if word.lower() not in data["words"]:
                data["words"][word.lower()] = {"word": word.lower()}
            
            data["words"][word.lower()]["chats"] = chats
            
            with open(self.jsonPath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            logger.info(f"✅ Saved {len(dialogues)} dialogues for '{word}'")
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error saving dialogues: {str(e)}")
            raise PipelineError("JSON_PARSE", f"Failed to parse word data JSON: {str(e)}", e)
        except Exception as e:
            logger.error(f"❌ Error saving dialogues: {str(e)}")
            raise PipelineError("JSON_SAVE", f"Failed to save dialogues: {str(e)}", e)
    
    def _updateAudioInJson(self, word: str, chatId: str, audioFile: str):
        """Update audio file in JSON with error handling"""
        try:
            if not os.path.exists(self.jsonPath):
                logger.warning(f"⚠️ Word data file not found for audio update: {self.jsonPath}")
                return
            
            with open(self.jsonPath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if word.lower() in data.get("words", {}) and chatId in data["words"][word.lower()].get("chats", {}):
                data["words"][word.lower()]["chats"][chatId]["audioFile"] = audioFile
                
                with open(self.jsonPath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                
                logger.info(f"✅ Updated audio for {word}/{chatId}: {audioFile}")
            else:
                logger.warning(f"⚠️ Chat not found for audio update: {word}/{chatId}")
                
        except Exception as e:
            logger.error(f"❌ Error updating audio in JSON: {str(e)}")
            # Don't raise error here as this is a non-critical update
    
    def _updateImageInJson(self, word: str, chatId: str, imageFile: str):
        """Update image file in JSON with error handling"""
        try:
            if not os.path.exists(self.jsonPath):
                logger.warning(f"⚠️ Word data file not found for image update: {self.jsonPath}")
                return
            
            with open(self.jsonPath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if word.lower() in data.get("words", {}) and chatId in data["words"][word.lower()].get("chats", {}):
                data["words"][word.lower()]["chats"][chatId]["imageFile"] = imageFile
                
                with open(self.jsonPath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                
                logger.info(f"✅ Updated image for {word}/{chatId}: {imageFile}")
            else:
                logger.warning(f"⚠️ Chat not found for image update: {word}/{chatId}")
                
        except Exception as e:
            logger.error(f"❌ Error updating image in JSON: {str(e)}")
            # Don't raise error here as this is a non-critical update
    
    def _updateFinalVideoInJson(self, word: str, videoPath: str):
        """Update final video path in JSON with error handling"""
        try:
            if not os.path.exists(self.jsonPath):
                logger.warning(f"⚠️ Word data file not found for video update: {self.jsonPath}")
                return
            
            with open(self.jsonPath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if word.lower() in data.get("words", {}):
                data["words"][word.lower()]["finalVideoFile"] = videoPath
                
                with open(self.jsonPath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                
                logger.info(f"✅ Updated final video path for {word}: {videoPath}")
            else:
                logger.warning(f"⚠️ Word not found for video update: {word}")
                
        except Exception as e:
            logger.error(f"❌ Error updating final video in JSON: {str(e)}")
            # Don't raise error here as this is a non-critical update
    
    def _loadWordData(self, word: str) -> Optional[Dict]:
        """Load word data from JSON with error handling"""
        try:
            if not os.path.exists(self.jsonPath):
                logger.error(f"❌ Word data file not found: {self.jsonPath}")
                return None
            
            with open(self.jsonPath, "r", encoding='utf-8') as f:
                data = json.load(f)
            
            word_data = data.get("words", {}).get(word.lower())
            if word_data:
                logger.info(f"✅ Loaded word data for '{word}'")
                return word_data
            else:
                logger.warning(f"⚠️ No data found for word '{word}'")
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error loading word data: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ Error loading word data: {str(e)}")
            return None
    
    def _getVideoDuration(self, videoPath: str) -> float:
        """Get video duration using ffprobe"""
        try:
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', videoPath
            ], capture_output=True, text=True)
            return float(result.stdout.strip()) if result.returncode == 0 else 3.0
        except:
            return 3.0

    def _removeExistingWordData(self, word: str):
        """Remove existing word data for fresh start and cleanup associated files"""
        try:
            if os.path.exists(self.jsonPath):
                with open(self.jsonPath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if word.lower() in data.get("words", {}):
                    wordData = data["words"][word.lower()]
                    
                    # Clean up associated audio files
                    audioFiles = []
                    if "chats" in wordData:
                        for chatId, chatData in wordData["chats"].items():
                            if "audioFile" in chatData:
                                audioFile = chatData["audioFile"]
                                if not audioFile.startswith("data/"):
                                    audioFile = f"data/{audioFile}"
                                audioFiles.append(audioFile)
                    
                    # Clean up final video file
                    videoFile = None
                    if "finalVideoFile" in wordData:
                        videoFile = wordData["finalVideoFile"]
                        if not videoFile.startswith("data/"):
                            videoFile = f"data/{videoFile}"
                    
                    # Remove files
                    cleanedFiles = []
                    for audioFile in audioFiles:
                        try:
                            if os.path.exists(audioFile):
                                os.remove(audioFile)
                                cleanedFiles.append(audioFile)
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to remove audio file {audioFile}: {str(e)}")
                    
                    if videoFile:
                        try:
                            if os.path.exists(videoFile):
                                os.remove(videoFile)
                                cleanedFiles.append(videoFile)
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to remove video file {videoFile}: {str(e)}")
                    
                    # Remove word from JSON
                    del data["words"][word.lower()]
                    
                    with open(self.jsonPath, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)
                    
                    logger.info(f"✅ Removed existing word data for '{word}' and cleaned {len(cleanedFiles)} associated files")
                    print(f"🧹 Cleaned existing data for '{word}' - removed {len(cleanedFiles)} files")
                else:
                    logger.info(f"⚠️ No existing data found for word '{word}' to remove")
                    print(f"⚠️ No existing data found for word '{word}' to remove")
            else:
                logger.info(f"⚠️ Word data file not found: {self.jsonPath}")
                print(f"⚠️ Word data file not found, will create fresh")
            
            # Clean up orphaned files that might contain the word name
            self._cleanupOrphanedFiles(word)
                
        except Exception as e:
            logger.error(f"❌ Error removing word data: {str(e)}")
            raise PipelineError("JSON_REMOVE", f"Failed to remove word data: {str(e)}", e)
    
    def _cleanupOrphanedFiles(self, word: str):
        """Clean up orphaned audio and video files that might contain the word name"""
        try:
            orphanedFiles = []
            
            # Check generated audio files
            generatedDir = "data/audio_files/generated"
            if os.path.exists(generatedDir):
                for file in os.listdir(generatedDir):
                    if word.lower() in file.lower() and file.endswith('.wav'):
                        filePath = os.path.join(generatedDir, file)
                        try:
                            os.remove(filePath)
                            orphanedFiles.append(filePath)
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to remove orphaned audio file {filePath}: {str(e)}")
            
            # Check video output files
            videoDir = "data/video_output"
            if os.path.exists(videoDir):
                for file in os.listdir(videoDir):
                    if word.lower() in file.lower() and (file.endswith('.mp4') or file.endswith('.wav')):
                        filePath = os.path.join(videoDir, file)
                        try:
                            os.remove(filePath)
                            orphanedFiles.append(filePath)
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to remove orphaned video/audio file {filePath}: {str(e)}")
            
            # Check for temporary files in root directory
            rootTempFiles = [
                "temp_single_audio.wav",
                f"{word.lower()}_combined_audio.wav",
                f"data/video_output/{word.lower()}_combined_audio.wav"
            ]
            
            for tempFile in rootTempFiles:
                try:
                    if os.path.exists(tempFile):
                        os.remove(tempFile)
                        orphanedFiles.append(tempFile)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to remove temp file {tempFile}: {str(e)}")
            
            if orphanedFiles:
                logger.info(f"✅ Cleaned {len(orphanedFiles)} orphaned files for '{word}'")
                print(f"🧹 Also cleaned {len(orphanedFiles)} orphaned files")
                
        except Exception as e:
            logger.warning(f"⚠️ Error cleaning orphaned files: {str(e)}")
            # Don't raise error here as this is cleanup, not critical


def getRandomBackgroundVideo():
    """Get a random background video from the background directory"""
    backgroundDir = "data/background"
    if os.path.exists(backgroundDir):
        backgroundFiles = [f for f in os.listdir(backgroundDir) 
                          if f.startswith('background') and f.endswith('.mp4')]
        if backgroundFiles:
            randomBackground = random.choice(backgroundFiles)
            backgroundVideo = os.path.join(backgroundDir, randomBackground)
            print(f"🎲 Randomly selected background: {randomBackground}")
            return backgroundVideo
        else:
            print("⚠️ No background videos found in data/background directory")
            return None
    else:
        print("⚠️ Background directory not found")
        return None


def bulkProcess():
    """Process all unused words from greWords.json in sorted key order with comprehensive error handling"""
    greWordsPath = "data/greWords.json"
    
    # Validate GRE words file exists
    if not os.path.exists(greWordsPath):
        logger.error(f"❌ {greWordsPath} not found")
        print(f"❌ {greWordsPath} not found")
        return False

    logger.info("🚀 Starting bulk processing mode...")
    print("🚀 Starting bulk processing mode...")

    try:
        processedCount = 0
        totalWords = 0
        
        while True:
            # Get random background video for each word
            try:
                backgroundVideo = getRandomBackgroundVideo()
                if not backgroundVideo:
                    logger.warning("⚠️ No background video available, using default")
                    backgroundVideo = "downloads/Minecraft Parkour Gameplay No Copyright_mobile.mp4"
                    if not os.path.exists(backgroundVideo):
                        logger.error(f"❌ Default background video not found: {backgroundVideo}")
                        print(f"❌ Default background video not found: {backgroundVideo}")
                        return False
            except Exception as e:
                logger.error(f"❌ Error getting background video: {str(e)}")
                return False
            
            # Load the entire GRE words file (reload each time to get updates)
            try:
                with open(greWordsPath, 'r', encoding='utf-8') as f:
                    greWords = json.load(f)
                
                if processedCount == 0:  # Only show this on first iteration
                    logger.info(f"📚 Loaded {len(greWords)} words from {greWordsPath}")
                    print(f"📚 Loaded {len(greWords)} words from {greWordsPath}")
                    totalWords = len(greWords)
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ Invalid JSON in {greWordsPath}: {str(e)}")
                print(f"❌ Invalid JSON in {greWordsPath}: {str(e)}")
                return False
            except Exception as e:
                logger.error(f"❌ Error loading {greWordsPath}: {str(e)}")
                print(f"❌ Error loading {greWordsPath}: {str(e)}")
                return False
            
            # Find the first unused word in sorted key order
            sortedKeys = sorted(greWords.keys(), key=int)
            firstUnusedWord = None
            firstUnusedKey = None
            
            for key in sortedKeys:
                wordData = greWords[key]
                if not wordData.get("used", False):
                    firstUnusedWord = wordData["word"]
                    firstUnusedKey = key
                    break
            
            if not firstUnusedWord:
                print(f"🎉 All words have been processed!")
                print(f"📊 Total processed in this session: {processedCount}")
                return True
            
            print(f"\n{'='*60}")
            print(f"🎯 Processing word {processedCount + 1}: {firstUnusedWord.upper()} (key: {firstUnusedKey})")
            if backgroundVideo:
                print(f"🎥 Using background: {os.path.basename(backgroundVideo)}")
            print(f"{'='*60}")
            
            # Initialize pipeline
            try:
                logger.info(f"Initializing pipeline for: {firstUnusedWord}")
                pipeline = UnifiedVideoPipeline()
            except Exception as e:
                logger.error(f"❌ Failed to initialize pipeline: {str(e)}")
                print(f"❌ Failed to initialize pipeline: {str(e)}")
                # Continue to next word instead of failing completely
                firstUnusedWord = None
                firstUnusedKey = None
            
            if firstUnusedWord:  # Only process if initialization succeeded
                # Process the word
                logger.info(f"🎬 Starting pipeline for: {firstUnusedWord.upper()}")
                print(f"🎬 Starting pipeline for: {firstUnusedWord.upper()}")
                
                try:
                    success = pipeline.run(firstUnusedWord, backgroundVideo)
                except Exception as e:
                    logger.error(f"❌ Pipeline execution failed for '{firstUnusedWord}': {str(e)}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    print(f"❌ Pipeline execution failed for '{firstUnusedWord}': {str(e)}")
                    success = False
            else:
                success = False
            
            if success:
                # Get the final video path from wordData.json
                finalVideoPath = None
                try:
                    with open("data/wordData.json", 'r', encoding='utf-8') as f:
                        wordData = json.load(f)
                    
                    if firstUnusedWord.lower() in wordData.get("words", {}):
                        finalVideoPath = wordData["words"][firstUnusedWord.lower()].get("finalVideoFile", "")
                except:
                    pass
                
                # Update the word data with detailed structure
                currentTime = datetime.now().isoformat() + 'Z'
                
                # Get the meaning from the original structure or use a default
                originalMeaning = greWords[firstUnusedKey].get("meaning", f"Learn the meaning of {firstUnusedWord}")
                
                greWords[firstUnusedKey] = {
                    "word": firstUnusedWord,
                    "meaning": originalMeaning,
                    "used": True,
                    "filename": finalVideoPath if finalVideoPath else f"data/video_output/{firstUnusedWord}_final_video.mp4",
                    "title": f"Today's Word! - {firstUnusedWord.upper()}",
                    "description": f"{firstUnusedWord.upper()} - {originalMeaning}   #GRE #Vocabulary #English #WordOfTheDay #Trending #IndiaSpeaks",
                    "youtubeUploaded": False,
                    "instagramUploaded": False,
                    "uploadTimestamp": None,
                    "createdAt": currentTime,
                    "videoChecked": False,
                    "retryCount": 0
                }
                
                # Save the entire updated file
                try:
                    with open(greWordsPath, 'w', encoding='utf-8') as f:
                        json.dump(greWords, f, indent=4, ensure_ascii=False)
                    logger.info(f"✅ Updated {greWordsPath} with detailed metadata for '{firstUnusedWord}'")
                except Exception as e:
                    logger.error(f"❌ Failed to save updated GRE words file: {str(e)}")
                    print(f"❌ Failed to save updated GRE words file: {str(e)}")
                    # Continue processing despite save error
                
                processedCount += 1
                print(f"✅ Successfully processed '{firstUnusedWord}' ({processedCount} completed)")
                print(f"📝 Updated {greWordsPath} with detailed metadata")
                
                # Show progress
                remaining = sum(1 for key in sortedKeys if not greWords[key].get("used", False))
                print(f"📊 Progress: {processedCount} completed, {remaining} remaining")
                
            else:
                print(f"❌ Failed to process '{firstUnusedWord}' - continuing to next word...")
                # Mark as used even if failed to avoid getting stuck
                currentTime = datetime.now().isoformat() + 'Z'
                
                originalMeaning = greWords[firstUnusedKey].get("meaning", f"Learn the meaning of {firstUnusedWord}")
                
                greWords[firstUnusedKey] = {
                    "word": firstUnusedWord,
                    "meaning": originalMeaning,
                    "used": True,  # Mark as used even if failed to avoid infinite loop
                    "filename": None,
                    "title": f"Today's Word! - {firstUnusedWord}",
                    "description": f"{firstUnusedWord} - {originalMeaning}",
                    "youtubeUploaded": False,
                    "instagramUploaded": False,
                    "uploadTimestamp": None,
                    "createdAt": currentTime,
                    "videoChecked": False,
                    "retryCount": 1  # Mark as failed attempt
                }
                
                try:
                    with open(greWordsPath, 'w', encoding='utf-8') as f:
                        json.dump(greWords, f, indent=4, ensure_ascii=False)
                    logger.info(f"Marked '{firstUnusedWord}' as failed in {greWordsPath}")
                except Exception as e:
                    logger.error(f"❌ Failed to save failed word status: {str(e)}")
                    print(f"❌ Failed to save failed word status: {str(e)}")
                
                processedCount += 1

    except KeyboardInterrupt:
        logger.info(f"\n⚠️ Bulk processing interrupted by user")
        print(f"\n⚠️ Bulk processing interrupted by user")
        print(f"📊 Processed {processedCount} words before interruption")
        logger.info(f"📊 Processed {processedCount} words before interruption")
        return True
    except Exception as e:
        logger.error(f"❌ Unexpected error during bulk processing: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        print(f"❌ Unexpected error during bulk processing: {str(e)}")
        print(f"📊 Processed {processedCount} words before error")
        logger.info(f"📊 Processed {processedCount} words before error")
        return False


def checkSystemRequirements():
    """Check system requirements and log status"""
    logger.info("🔍 Checking system requirements...")
    
    # Check if FFmpeg is available
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            logger.info("✅ FFmpeg is available")
        else:
            logger.error("❌ FFmpeg check failed")
            return False
    except subprocess.TimeoutExpired:
        logger.error("❌ FFmpeg check timed out")
        return False
    except FileNotFoundError:
        logger.error("❌ FFmpeg not found in PATH")
        return False
    except Exception as e:
        logger.error(f"❌ Error checking FFmpeg: {str(e)}")
        return False
    
    # Check required directories
    required_dirs = ["data", "data/audio_files", "data/audio_files/generated", "data/background", "data/images"]
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            logger.warning(f"⚠️ Directory not found: {dir_path}")
            try:
                os.makedirs(dir_path, exist_ok=True)
                logger.info(f"✅ Created directory: {dir_path}")
            except Exception as e:
                logger.error(f"❌ Failed to create directory {dir_path}: {str(e)}")
                return False
        else:
            logger.info(f"✅ Directory exists: {dir_path}")
    
    # Check required files
    required_files = ["data/userProfiles.json"]
    for file_path in required_files:
        if not os.path.exists(file_path):
            logger.error(f"❌ Required file not found: {file_path}")
            return False
        else:
            logger.info(f"✅ Required file exists: {file_path}")
    
    logger.info("✅ System requirements check completed")
    return True

def main():
    """Main entry point with system checks"""
    # Check system requirements first
    if not checkSystemRequirements():
        logger.error("❌ System requirements check failed")
        print("❌ System requirements check failed. Check logs for details.")
        sys.exit(1)
    
    # Check for bulk processing (both --bulk and -b)
    if "--bulk" in sys.argv or "-b" in sys.argv:
        logger.info("🚀 Starting bulk processing mode...")
        print("🚀 Starting bulk processing mode...")
        success = bulkProcess()
        
        if not success:
            logger.error("❌ Bulk processing failed")
            sys.exit(1)
        return
    
    # Regular single word processing
    try:
        # Get word input
        if len(sys.argv) > 1:
            word = sys.argv[1]
        else:
            word = input("Enter word: ").strip()
        
        if not word:
            logger.error("❌ No word provided")
            print("❌ No word provided")
            sys.exit(1)
        
        logger.info(f"Single word processing requested: {word}")
        
        # Get random background video for single word processing
        try:
            backgroundVideo = getRandomBackgroundVideo()
            if not backgroundVideo:
                logger.warning("⚠️ No background video available, using default")
                backgroundVideo = "downloads/Minecraft Parkour Gameplay No Copyright_mobile.mp4"
                if not os.path.exists(backgroundVideo):
                    logger.error(f"❌ Default background video not found: {backgroundVideo}")
                    print(f"❌ Default background video not found: {backgroundVideo}")
                    sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Error getting background video: {str(e)}")
            print(f"❌ Error getting background video: {str(e)}")
            sys.exit(1)
        
        logger.info(f"🎬 Processing single word: {word.upper()}")
        print(f"🎬 Processing single word: {word.upper()}")
        if backgroundVideo:
            logger.info(f"🎥 Using background: {os.path.basename(backgroundVideo)}")
            print(f"🎥 Using background: {os.path.basename(backgroundVideo)}")
        
        # Run pipeline
        try:
            pipeline = UnifiedVideoPipeline()
            success = pipeline.run(word, backgroundVideo)
            
            if success:
                logger.info(f"✅ Single word processing completed successfully for '{word}'")
                print(f"✅ Single word processing completed successfully for '{word}'")
            else:
                logger.error(f"❌ Single word processing failed for '{word}'")
                print(f"❌ Single word processing failed for '{word}'")
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"❌ Unexpected error in single word processing: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            print(f"❌ Unexpected error in single word processing: {str(e)}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("⚠️ Single word processing interrupted by user")
        print("\n⚠️ Processing interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Unexpected error in main: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 