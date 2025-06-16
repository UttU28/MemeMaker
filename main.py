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

from dotenv import load_dotenv
from src.client import F5TtsGradioClient
from src.config import ConfigManager
from src.utils import AudioFileManager
from src.llm import LlmService
from prompts import CHAT_GENERATION_PROMPT, GET_THE_MOOD_PROMPT

warnings.filterwarnings("ignore", category=UserWarning)
load_dotenv()


class UnifiedVideoPipeline:
    """Complete end-to-end pipeline for video generation from a single word"""
    
    def __init__(self):
        self.llmService = LlmService()
        self.configManager = ConfigManager()
        self.audioManager = AudioFileManager()
        self.jsonPath = "data/wordData.json"
        self.videoOutputDir = "data/video_output"
        os.makedirs(self.videoOutputDir, exist_ok=True)
    
    def run(self, word: str, backgroundVideo: str = None):
        """Main pipeline execution"""
        print(f"🎬 Starting pipeline for: {word.upper()}")
        
        if not self._checkServices():
            return False
        
        # Step 1: Generate dialogue
        dialogues = self._generateAndSaveDialogue(word)
        if not dialogues:
            return False
        
        # Step 2: Generate audio for each dialogue
        audioFiles = self._generateAudioFiles(word, dialogues)
        
        # Step 3: Detect moods and assign images
        self._detectMoodsAndAssignImages(word, dialogues)
        
        # Step 4: Generate final video
        success = self._generateVideo(word, backgroundVideo)
        
        if success:
            print(f"✅ Pipeline completed successfully for '{word}'")
        
        return success
    
    def _checkServices(self) -> bool:
        """Check if required services are running"""
        try:
            response = requests.get("http://localhost:7860/", timeout=5)
            if response.status_code != 200:
                print("❌ Gradio endpoint not running")
                return False
        except:
            print("❌ Gradio endpoint not accessible")
            return False
        
        return True
    
    def _generateAndSaveDialogue(self, word: str) -> List[Tuple[str, str, str]]:
        """Generate dialogue and save to JSON"""
        # Generate dialogue using LLM
        prompt = CHAT_GENERATION_PROMPT.format(word=word.capitalize())
        dialogue = self.llmService.generate(prompt, provider="openai")
        
        if not dialogue:
            print("❌ Failed to generate dialogue")
            return []
        
        dialogue = self.llmService.cleanResponse(dialogue)
        
        # Parse dialogue
        dialogues = []
        for line in dialogue.split("\n"):
            if not line.strip():
                continue
            
            try:
                personName = line.split("}")[0].split("{")[1]
                lineText = line.split("}")[1].strip()
                userId = self._getUserId(personName)
                
                if userId:
                    dialogues.append((lineText, personName, userId))
            except:
                continue
        
        if not dialogues:
            print("❌ No valid dialogues parsed")
            return []
        
        # Save to JSON
        self._initializeWordData(word)
        self._saveDialoguesToJson(word, dialogues)
        
        return dialogues
    
    def _generateAudioFiles(self, word: str, dialogues: List[Tuple[str, str, str]]) -> int:
        """Generate audio files for all dialogues"""
        client = F5TtsGradioClient()
        audioCount = 0
        
        if not client.connectToGradio():
            return 0
        
        try:
            for i, (lineText, personName, userId) in enumerate(dialogues, 1):
                chatId = f"chat{i}"
                
                # Generate audio
                success = client.generateSpeechWithUser(userId, lineText)
                
                if success:
                    # Get generated file
                    outputPrefix = self.configManager.getOutputPrefixWithFallback(userId)
                    generatedFiles = self.audioManager.listGeneratedFiles(outputPrefix)
                    
                    if generatedFiles:
                        audioFileName = generatedFiles[0]
                        
                        # Clean audio
                        cleanedFileName = self._cleanAudioFile(audioFileName)
                        if cleanedFileName:
                            audioPath = f"audio_files/generated/{cleanedFileName}"
                            self._updateAudioInJson(word, chatId, audioPath)
                            audioCount += 1
        finally:
            client.close()
        
        return audioCount
    
    def _detectMoodsAndAssignImages(self, word: str, dialogues: List[Tuple[str, str, str]]):
        """Detect moods and assign images for dialogues"""
        if not self.llmService.isOllamaRunning():
            return
        
        with open("data/userProfiles.json", "r") as f:
            profiles = json.load(f)
        
        for i, (lineText, personName, userId) in enumerate(dialogues, 1):
            chatId = f"chat{i}"
            
            # Get available emotions for speaker
            speaker = personName.lower()
            if speaker in profiles["users"]:
                emotions = profiles["users"][speaker]["emotions"]
                expressions = list(emotions.keys())
            else:
                continue
            
            # Detect mood
            options = ", ".join(expressions)
            prompt = GET_THE_MOOD_PROMPT.format(sentence=lineText, options=options)
            response = self.llmService.generate(prompt, provider="ollama", model="llama3.2")
            
            if response and response.strip().lower() in [exp.lower() for exp in expressions]:
                mood = response.strip().lower()
                imageFile = emotions[mood]
                self._updateImageInJson(word, chatId, imageFile)
    
    def _generateVideo(self, word: str, backgroundVideo: str = None) -> bool:
        """Generate final video with subtitles"""
        wordData = self._loadWordData(word)
        if not wordData:
            return False
        
        # Validate and fill missing images before processing
        self._validateAndFillMissingImages(word, wordData)
        # Reload word data after potential updates
        wordData = self._loadWordData(word)
        if not wordData:
            return False
        
        if not backgroundVideo:
            backgroundVideo = r"downloads/Minecraft Parkour Gameplay No Copyright_mobile.mp4"
        
        if not os.path.exists(backgroundVideo):
            print(f"❌ Background video not found")
            return False
        
        # Create timeline
        timeline, totalDuration = self._createTimeline(wordData)
        if not timeline:
            return False
        
        # Concatenate audio
        combinedAudioPath = f"{self.videoOutputDir}/{word}_combined_audio.wav"
        if not self._concatenateAudioFiles(timeline, combinedAudioPath):
            return False
        
        # Generate final video with subtitles
        finalVideoPath = f"{self.videoOutputDir}/{word}_final_video.mp4"
        if not self._generateBaseVideo(backgroundVideo, timeline, totalDuration, 
                                     combinedAudioPath, finalVideoPath, word):
            return False
        
        # Update final video path in JSON
        self._updateFinalVideoInJson(word, finalVideoPath)
        
        # Cleanup temp files
        for tempFile in [combinedAudioPath]:
            if os.path.exists(tempFile):
                os.remove(tempFile)
        
        return True
    
    def _validateAndFillMissingImages(self, word: str, wordData: Dict):
        """Validate and fill missing image files with default confident emotion images"""
        try:
            # Load user profiles
            with open("data/userProfiles.json", "r") as f:
                profiles = json.load(f)
            
            chats = wordData.get("chats", {})
            needsUpdate = False
            
            for chatId, chatData in chats.items():
                speaker = chatData.get("speaker", "").lower()
                imageFile = chatData.get("imageFile", "")
                
                # Check if image file is missing or doesn't exist
                if not imageFile or not os.path.exists(imageFile):
                    print(f"🔍 Missing image for {chatId} (speaker: {speaker}), looking for default...")
                    
                    # Find speaker in profiles
                    if speaker in profiles.get("users", {}):
                        userEmotions = profiles["users"][speaker].get("emotions", {})
                        
                        # Try to get confident emotion as default
                        if "confident" in userEmotions:
                            defaultImage = userEmotions["confident"]
                            
                            # Verify the default image exists
                            if os.path.exists(defaultImage):
                                print(f"✅ Using default confident image for {speaker}: {defaultImage}")
                                chatData["imageFile"] = defaultImage
                                needsUpdate = True
                            else:
                                print(f"⚠️ Default confident image not found for {speaker}: {defaultImage}")
                        else:
                            # If no confident emotion, try to get any available emotion
                            if userEmotions:
                                firstEmotion = list(userEmotions.keys())[0]
                                defaultImage = userEmotions[firstEmotion]
                                
                                if os.path.exists(defaultImage):
                                    print(f"✅ Using {firstEmotion} image for {speaker}: {defaultImage}")
                                    chatData["imageFile"] = defaultImage
                                    needsUpdate = True
                                else:
                                    print(f"⚠️ No valid images found for speaker: {speaker}")
                            else:
                                print(f"⚠️ No emotions defined for speaker: {speaker}")
                    else:
                        print(f"⚠️ Speaker '{speaker}' not found in user profiles")
            
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
                except Exception as e:
                    print(f"❌ Failed to update word data: {e}")
                    
        except Exception as e:
            print(f"❌ Error validating images: {e}")
    
    def _cleanAudioFile(self, audioFileName: str) -> Optional[str]:
        """Clean audio file by trimming silence"""
        inputPath = self.audioManager.getGeneratedFilePath(audioFileName)
        
        if not os.path.exists(inputPath):
            return None
        
        try:
            audio = AudioSegment.from_file(inputPath)
            
            # Detect non-silent chunks
            chunks = silence.detect_nonsilent(
                audio,
                min_silence_len=100,
                silence_thresh=-40
            )
            
            if not chunks:
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
            
            return cleanedFileName
            
        except Exception:
            return None
    
    def _generateSingleSubtitle(self, audioFile: str, dialogue: str) -> Optional[Dict]:
        """Generate subtitle information for a single audio clip"""
        device = "cpu"
        tempAudioPath = "temp_single_audio.wav"
        
        try:
            # Copy audio file to temp location
            if not audioFile.startswith('data/'):
                audioFile = 'data/' + audioFile
            audio = AudioSegment.from_file(audioFile)
            audio.export(tempAudioPath, format="wav")
            
            # Transcribe with Whisper (explicitly set to English)
            whisperModel = whisperx.load_model("base", device, compute_type="float32")
            transcription = whisperModel.transcribe(
                tempAudioPath,
                batch_size=1,
                language="en",  # Explicitly set to English
                task="transcribe"  # Force transcription task
            )
            
            if not transcription.get("segments"):
                return None
            
            # Align words (explicitly set to English)
            alignModel, metadata = whisperx.load_align_model(
                language_code="en",
                device=device,
                model_name="WAV2VEC2_ASR_LARGE_LV60K_960H"  # More accurate English model
            )
            alignedData = whisperx.align(
                transcription["segments"],
                alignModel,
                metadata,
                tempAudioPath,
                device,
                return_char_alignments=False  # We don't need character-level alignment
            )
            
            if not alignedData.get("word_segments"):
                return None
            
            # Parse original dialogue text into words
            originalWords = []
            cleanLine = re.sub(r'[^\w\s]', '', dialogue.strip())
            words = cleanLine.split()
            originalWords.extend(words)
            
            # Create subtitle segments
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
                subtitleSegments.append({
                    "start": start,
                    "end": end,
                    "text": text
                })
            
            return {
                "segments": subtitleSegments,
                "duration": len(audio) / 1000.0  # Convert to seconds
            }
            
        except Exception as e:
            print(f"❌ Error generating subtitle: {e}")
            return None
        finally:
            if os.path.exists(tempAudioPath):
                os.remove(tempAudioPath)

    def _createTimeline(self, wordData: Dict) -> Tuple[List[Dict], float]:
        """Create timeline for video generation"""
        chats = wordData["chats"]
        timeline = []
        currentTime = 0
        
        for chatId in sorted(chats.keys(), key=lambda x: int(x.replace('chat', ''))):
            chatData = chats[chatId]
            audioFile = chatData.get("audioFile", "")
            
            if not audioFile:
                continue
            
            # Generate subtitle information for this clip
            subtitleInfo = self._generateSingleSubtitle(audioFile, chatData["dialogue"])
            if not subtitleInfo:
                continue
            
            timeline.append({
                "chatId": chatId,
                "speaker": chatData["speaker"],
                "dialogue": chatData["dialogue"],
                "audioFile": audioFile,
                "imageFile": chatData.get("imageFile", ""),
                "startTime": currentTime,
                "endTime": currentTime + subtitleInfo["duration"],
                "duration": subtitleInfo["duration"],
                "subtitleSegments": subtitleInfo["segments"]
            })
            
            currentTime += subtitleInfo["duration"]
        
        return timeline, currentTime
    
    def _concatenateAudioFiles(self, timeline: List[Dict], outputPath: str) -> bool:
        """Concatenate audio files"""
        try:
            combinedAudio = AudioSegment.empty()
            
            for item in timeline:
                audioFile = item["audioFile"]
                if not audioFile.startswith('data/'):
                    audioFile = 'data/' + audioFile
                audio = AudioSegment.from_file(audioFile)
                combinedAudio += audio
            
            combinedAudio.export(outputPath, format="wav")
            return True
        except:
            return False
    
    def _generateBaseVideo(self, backgroundVideo: str, timeline: List[Dict], 
                          totalDuration: float, combinedAudio: str, outputVideo: str, word: str) -> bool:
        """Generate base video with FFmpeg"""
        # Check for outro
        outroPath = "data/outro.mp4"
        useOutro = os.path.exists(outroPath)
        
        # Build FFmpeg command
        filterParts = []
        inputParts = ['-hwaccel', 'cuda', '-stream_loop', '-1', '-i', backgroundVideo, '-i', combinedAudio]
        
        if useOutro:
            inputParts.extend(['-i', outroPath])
            inputIndex = 3
        else:
            inputIndex = 2
        
        # Add image inputs
        imageInputs = {}
        for item in timeline:
            if item["imageFile"] and os.path.exists(item["imageFile"]):
                inputParts.extend(['-i', item["imageFile"]])
                imageInputs[item["chatId"]] = inputIndex
                inputIndex += 1
        
        # Build filter complex
        filterParts.append(f"[0:v]scale=1080:1920:force_original_aspect_ratio=disable,setsar=1,trim=duration={totalDuration},setpts=PTS-STARTPTS[bg]")
        currentBase = "[bg]"
        
        # Add overlays and subtitles
        for i, item in enumerate(timeline):
            if item["chatId"] in imageInputs:
                imgInput = imageInputs[item["chatId"]]
                # Add image overlay
                filterParts.append(
                    f"{currentBase}[{imgInput}:v]overlay=0:0:enable='between(t,{item['startTime']},{item['endTime']})'[overlay{i}]"
                )
                currentBase = f"[overlay{i}]"
            
            # Add subtitles for this segment
            if "subtitleSegments" in item:
                for segment in item["subtitleSegments"]:
                    start = item["startTime"] + segment["start"]
                    end = item["startTime"] + segment["end"]
                    text = segment["text"]
                    # Escape special characters in text
                    text = text.replace("'", "\\'").replace('"', '\\"')
                    filterParts.append(
                        f"{currentBase}drawtext=text='{text}':fontfile='C\\:/Windows/Fonts/impact.ttf':fontsize=64:fontcolor=white:x=(w-text_w)/2:y=h-th-50:enable='between(t,{start},{end})'[sub{i}]"
                    )
                    currentBase = f"[sub{i}]"
        
        # Add main title overlays (Today's Word and the word itself)
        mainWord = word.upper()
        # Add "Today's Word!" title
        filterParts.append(
            f"{currentBase}drawtext=text='Todays Word!':fontfile='C\\:/Windows/Fonts/impact.ttf':fontsize=60:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=80[title]"
        )
        # Add the main word
        filterParts.append(
            f"[title]drawtext=text='{mainWord}':fontfile='C\\:/Windows/Fonts/impact.ttf':fontsize=140:fontcolor=yellow:borderw=6:bordercolor=black:x=(w-text_w)/2:y=140[word_overlay]"
        )
        currentBase = "[word_overlay]"
        
        # Add outro if exists
        if useOutro:
            filterParts.append(f"[2:v]scale=1080:1920:force_original_aspect_ratio=disable,setsar=1[outro_scaled]")
            filterParts.append(f"{currentBase}[outro_scaled]concat=n=2:v=1:a=0[final_video]")
            
            # Handle audio
            outroDuration = self._getVideoDuration(outroPath)
            filterParts.append(f"anullsrc=channel_layout=mono:sample_rate=24000[silence]")
            filterParts.append(f"[1:a][silence]concat=n=2:v=0:a=1[temp_audio]")
            filterParts.append(f"[temp_audio]atrim=duration={totalDuration + outroDuration}[final_audio]")
            outputMapping = ['-map', '[final_video]', '-map', '[final_audio]']
        else:
            filterParts.append(f"{currentBase}setpts=PTS-STARTPTS[final_video]")
            outputMapping = ['-map', '[final_video]', '-map', '1:a']
        
        filterComplex = ";".join(filterParts)
        
        # Execute FFmpeg
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
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _addSubtitles(self, dialogueText: str, videoPath: str, outputPath: str, word: str) -> bool:
        """Add subtitles and word overlay to video"""
        device = "cpu"
        audioPath = "temp_audio.wav"
        srtPath = "subtitles.srt"
        
        # Extract audio
        if not self._extractAudio(videoPath, audioPath):
            return False
        
        try:
            # Transcribe with Whisper (only for timing information)
            whisperModel = whisperx.load_model("base", device, compute_type="float32")
            transcription = whisperModel.transcribe(audioPath, batch_size=1)
            
            if not transcription.get("segments"):
                return False
            
            # Align words
            alignModel, metadata = whisperx.load_align_model(language_code="en", device=device)
            alignedData = whisperx.align(transcription["segments"], alignModel, metadata, audioPath, device)
            
            if not alignedData.get("word_segments"):
                return False
            
            # Parse original dialogue text into words
            originalWords = []
            for line in dialogueText.split('\n'):
                if line.strip():
                    # Remove punctuation and split into words
                    cleanLine = re.sub(r'[^\w\s]', '', line.strip())
                    words = cleanLine.split()
                    originalWords.extend(words)
            
            print(f"📝 Original words count: {len(originalWords)}")
            print(f"🎤 Whisper words count: {len(alignedData['word_segments'])}")
            
            # Create SRT using original text with Whisper timing
            with open(srtPath, 'w', encoding='utf-8') as srtFile:
                wordSegments = alignedData["word_segments"]
                groupSize = 4
                
                for i in range(0, len(wordSegments), groupSize):
                    group = wordSegments[i:i+groupSize]
                    start = self._formatTime(group[0]['start'])
                    end = self._formatTime(group[-1]['end'])
                    
                    # Use original words instead of Whisper transcribed words
                    groupWords = []
                    for j, segment in enumerate(group):
                        originalIndex = i + j
                        if originalIndex < len(originalWords):
                            groupWords.append(originalWords[originalIndex])
                        else:
                            # Fallback to Whisper word if original words are exhausted
                            groupWords.append(segment['word'].strip())
                    
                    text = " ".join([w for w in groupWords if w])
                    text = f"<font face='Impact' size='16' color='&HFFFFFF&'>{text}</font>"
                    
                    srtFile.write(f"{i//groupSize + 1}\n{start} --> {end}\n{text}\n\n")
            
            # Apply subtitles and overlays
            subtitleStyle = "FontName=Impact,FontSize=16,PrimaryColour=&HFFFFFF&,BorderStyle=1,Outline=1,BackColour=&H80000000&,Bold=1,MarginV=25"
            mainWord = word.upper()
            
            videoFilter = f"subtitles={srtPath}:force_style='{subtitleStyle}',drawtext=text='Todays Word!':fontfile='C\\:/Windows/Fonts/impact.ttf':fontsize=60:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=80,drawtext=text='{mainWord}':fontfile='C\\:/Windows/Fonts/impact.ttf':fontsize=140:fontcolor=yellow:borderw=6:bordercolor=black:x=(w-text_w)/2:y=140"
            
            result = subprocess.run([
                "ffmpeg", "-y", "-hwaccel", "cuda", "-i", videoPath, 
                "-vf", videoFilter, 
                "-c:v", "h264_nvenc", "-preset", "fast", 
                outputPath
            ], capture_output=True, text=True)
            
            # Cleanup
            for file in [audioPath, srtPath]:
                if os.path.exists(file):
                    os.remove(file)
            
            return result.returncode == 0
            
        except Exception:
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
        """Initialize word data in JSON"""
        try:
            if os.path.exists(self.jsonPath):
                with open(self.jsonPath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {"words": {}}
            
            data["words"][word.lower()] = {
                "word": word.lower(),
                "chats": {}
            }
            
            with open(self.jsonPath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except:
            pass
    
    def _saveDialoguesToJson(self, word: str, dialogues: List[Tuple[str, str, str]]):
        """Save dialogues to JSON"""
        try:
            with open(self.jsonPath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            chats = {}
            for i, (lineText, personName, userId) in enumerate(dialogues, 1):
                chats[f"chat{i}"] = {
                    "dialogue": lineText,
                    "speaker": personName.lower()
                }
            
            data["words"][word.lower()]["chats"] = chats
            
            with open(self.jsonPath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except:
            pass
    
    def _updateAudioInJson(self, word: str, chatId: str, audioFile: str):
        """Update audio file in JSON"""
        try:
            with open(self.jsonPath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if word.lower() in data["words"] and chatId in data["words"][word.lower()]["chats"]:
                data["words"][word.lower()]["chats"][chatId]["audioFile"] = audioFile
            
            with open(self.jsonPath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except:
            pass
    
    def _updateImageInJson(self, word: str, chatId: str, imageFile: str):
        """Update image file in JSON"""
        try:
            with open(self.jsonPath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if word.lower() in data["words"] and chatId in data["words"][word.lower()]["chats"]:
                data["words"][word.lower()]["chats"][chatId]["imageFile"] = imageFile
            
            with open(self.jsonPath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except:
            pass
    
    def _updateFinalVideoInJson(self, word: str, videoPath: str):
        """Update final video path in JSON"""
        try:
            with open(self.jsonPath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if word.lower() in data["words"]:
                data["words"][word.lower()]["finalVideoFile"] = videoPath
            
            with open(self.jsonPath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except:
            pass
    
    def _loadWordData(self, word: str) -> Optional[Dict]:
        """Load word data from JSON"""
        try:
            with open(self.jsonPath, "r") as f:
                data = json.load(f)
            return data["words"].get(word.lower())
        except:
            return None
    
    def _getDialogueText(self, wordData: Dict) -> str:
        """Get dialogue text for subtitles"""
        dialogues = []
        sortedChats = sorted(wordData['chats'].keys(), key=lambda x: int(x.replace('chat', '')))
        
        for chatKey in sortedChats:
            chat = wordData['chats'][chatKey]
            if 'dialogue' in chat:
                dialogues.append(chat['dialogue'])
        
        return "\n".join(dialogues)
    
    def _getAudioDuration(self, audioFile: str) -> float:
        """Get audio duration in seconds"""
        try:
            if not audioFile.startswith('data/'):
                audioFile = 'data/' + audioFile
            audio = AudioSegment.from_file(audioFile)
            return len(audio) / 1000.0
        except:
            return 0
    
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
    
    def _extractAudio(self, videoPath: str, audioPath: str) -> bool:
        """Extract audio from video"""
        cmd = ["ffmpeg", "-y", "-i", videoPath, "-vn", "-acodec", "pcm_s16le", 
               "-ar", "16000", "-ac", "1", audioPath]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _formatTime(self, seconds: float) -> str:
        """Format seconds to SRT time format"""
        millis = int((seconds - int(seconds)) * 1000)
        seconds = int(seconds)
        mins, secs = divmod(seconds, 60)
        hours, mins = divmod(mins, 60)
        return f"{hours:02}:{mins:02}:{secs:02},{millis:03}"


def get_random_background_video():
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


def bulk_process():
    """Process all unused words from greWords.json in sorted key order"""
    greWordsPath = "data/greWords.json"
    
    if not os.path.exists(greWordsPath):
        print(f"❌ {greWordsPath} not found")
        return False

    try:
        processedCount = 0
        totalWords = 0
        
        while True:
            # Get random background video for each word
            backgroundVideo = get_random_background_video()
            
            # Load the entire GRE words file (reload each time to get updates)
            with open(greWordsPath, 'r', encoding='utf-8') as f:
                greWords = json.load(f)
            
            if processedCount == 0:  # Only show this on first iteration
                print(f"📚 Loaded {len(greWords)} words from {greWordsPath}")
                totalWords = len(greWords)
            
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
            pipeline = UnifiedVideoPipeline()
            
            # Process the word
            print(f"🎬 Starting pipeline for: {firstUnusedWord.upper()}")
            
            success = pipeline.run(firstUnusedWord, backgroundVideo)
            
            if success:
                # Update the word data in memory
                greWords[firstUnusedKey]["used"] = True
                
                # Try to get the final video path from wordData.json
                try:
                    with open("data/wordData.json", 'r', encoding='utf-8') as f:
                        wordData = json.load(f)
                    
                    if firstUnusedWord.lower() in wordData.get("words", {}):
                        finalVideo = wordData["words"][firstUnusedWord.lower()].get("finalVideoFile", "")
                        if finalVideo:
                            greWords[firstUnusedKey]["finalVideoFile"] = finalVideo
                except:
                    pass
                
                # Save the entire updated file
                with open(greWordsPath, 'w', encoding='utf-8') as f:
                    json.dump(greWords, f, indent=4, ensure_ascii=False)
                
                processedCount += 1
                print(f"✅ Successfully processed '{firstUnusedWord}' ({processedCount} completed)")
                print(f"📝 Updated {greWordsPath}")
                
                # Show progress
                remaining = sum(1 for key in sortedKeys if not greWords[key].get("used", False))
                print(f"📊 Progress: {processedCount} completed, {remaining} remaining")
                
            else:
                print(f"❌ Failed to process '{firstUnusedWord}' - continuing to next word...")
                # Mark as used even if failed to avoid getting stuck
                greWords[firstUnusedKey]["used"] = True
                with open(greWordsPath, 'w', encoding='utf-8') as f:
                    json.dump(greWords, f, indent=4, ensure_ascii=False)
                processedCount += 1

            break
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Bulk processing interrupted by user")
        print(f"📊 Processed {processedCount} words before interruption")
        return True
    except Exception as e:
        print(f"❌ Error during bulk processing: {e}")
        print(f"📊 Processed {processedCount} words before error")
        return False


def main():
    """Main entry point"""
    # Check for bulk processing (both --bulk and -b)
    if "--bulk" in sys.argv or "-b" in sys.argv:
        print("🚀 Starting bulk processing mode...")
        success = bulk_process()
        
        if not success:
            sys.exit(1)
        return
    
    # Regular single word processing
    # Get word input
    if len(sys.argv) > 1:
        word = sys.argv[1]
    else:
        word = input("Enter word: ").strip()
    
    if not word:
        print("❌ No word provided")
        sys.exit(1)
    
    # Get random background video for single word processing
    backgroundVideo = get_random_background_video()
    
    print(f"🎬 Processing single word: {word.upper()}")
    if backgroundVideo:
        print(f"🎥 Using background: {os.path.basename(backgroundVideo)}")
    
    # Run pipeline
    pipeline = UnifiedVideoPipeline()
    success = pipeline.run(word, backgroundVideo)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main() 