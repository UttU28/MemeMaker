import os
import time
import shutil
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import HTTPException
from gradio_client import Client, handle_file
from models import AudioGenerationResponse

logger = logging.getLogger(__name__)

def checkF5ttsConnection(f5ttsUrl: str = "http://localhost:7860") -> bool:
    try:
        import requests
        response = requests.get(f5ttsUrl, timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"💥 F5-TTS connection failed: {str(e)}")
        return False

def generateAudioFilename(scriptId: str, lineIndex: int, speaker: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safeSpeaker = speaker.lower().replace(' ', '_').replace('-', '_')
    return f"{scriptId}_line{lineIndex}_{safeSpeaker}_{timestamp}.wav"

class F5TTSClient:
    def __init__(self, url: str = "http://localhost:7860"):
        self.url = url
        self.client = None
        
    def connect(self) -> bool:
        try:
            self.client = Client(self.url)
            logger.info(f"🔗 Connected to F5-TTS API: {self.url}")
            return True
        except Exception as e:
            logger.error(f"💥 Failed to connect to F5-TTS: {str(e)}")
            return False
    
    def generateSpeech(self, audioFilePath: str, text: str, config: Dict[str, Any]) -> Optional[str]:
        if not self.client:
            logger.error("❌ Not connected to F5-TTS API")
            return None
        
        try:
            if not os.path.exists(audioFilePath):
                logger.error(f"❌ Audio file not found: {audioFilePath}")
                return None
            
            if not text or not text.strip():
                logger.error("❌ Empty text provided")
                return None
            
            text = text.strip()
            logger.info(f"🎤 Generating speech: {text[:50]}...")
            
            startTime = time.time()
            
            result = self.client.predict(
                ref_audio_input=handle_file(os.path.abspath(audioFilePath)),
                ref_text_input="",
                gen_text_input=text,
                remove_silence=config.get("removeSilences", True),
                randomize_seed=True,
                seed_input=0,
                cross_fade_duration_slider=config.get("crossFadeDuration", 0.15),
                nfe_slider=int(config.get("nfeSteps", 34)),
                speed_slider=config.get("speed", 1.0),
                api_name="/basic_tts"
            )
            
            duration = time.time() - startTime
            
            if result is None:
                logger.error("❌ F5-TTS returned None")
                return None
            
            audioPath = None
            if isinstance(result, tuple) and len(result) > 0:
                audioPath = result[0]
            elif isinstance(result, str):
                audioPath = result
            else:
                logger.error(f"❌ Unexpected result format: {type(result)}")
                return None
            
            if not audioPath or not os.path.exists(audioPath):
                logger.error(f"❌ Invalid audio path: {audioPath}")
                return None
            
            fileSize = os.path.getsize(audioPath)
            if fileSize == 0:
                logger.error(f"❌ Empty audio file: {audioPath}")
                return None
            
            logger.info(f"✅ Speech generated in {duration:.2f}s ({fileSize} bytes)")
            return audioPath
                
        except Exception as e:
            logger.error(f"❌ Speech generation failed: {str(e)}")
            return None
    
    def close(self):
        if self.client:
            self.client = None
            logger.info("📤 F5-TTS connection closed")

async def generateAudioForScript(scriptId: str, scriptsData: Dict, userProfiles: Dict, 
                                generatedAudioDir: str, progress_callback=None) -> AudioGenerationResponse:
    """Generate audio files for all dialogue lines in a script"""
    try:
        scripts = scriptsData.get("scripts", {})
        
        if scriptId not in scripts:
            raise HTTPException(status_code=404, detail=f"Script '{scriptId}' not found")
        
        script = scripts[scriptId]
        dialogueLines = script.get("dialogue", [])
        
        if not dialogueLines:
            raise HTTPException(status_code=400, detail="Script has no dialogue lines")
        
        if not checkF5ttsConnection():
            raise HTTPException(status_code=503, detail="F5-TTS service is not available")
        
        users = userProfiles.get("users", {})
        
        f5ttsClient = F5TTSClient()
        if not f5ttsClient.connect():
            raise HTTPException(status_code=503, detail="Failed to connect to F5-TTS service")
        
        try:
            totalLines = len(dialogueLines)
            processedLines = 0
            completedLines = 0
            failedLines = 0
            
            print(f"🎵 Starting audio generation for {totalLines} lines")
            
            updatedDialogue = []
            
            for lineIndex, dialogueLine in enumerate(dialogueLines):
                try:
                    speaker = dialogueLine.get("speaker", "").lower()
                    text = dialogueLine.get("text", "").strip()
                    existingAudio = dialogueLine.get("audioFile", "")
                    
                    updatedLine = {
                        "speaker": dialogueLine.get("speaker", ""),
                        "text": text,
                        "audioFile": existingAudio if existingAudio else ""
                    }
                    
                    if not speaker or not text:
                        failedLines += 1
                        processedLines += 1
                        updatedDialogue.append(updatedLine)
                        
                        # Call progress callback if provided
                        if progress_callback:
                            progress_percent = (processedLines / totalLines) * 100
                            progress_callback(progress_percent, f"Processed line {processedLines}/{totalLines} (invalid)")
                        
                        continue
                    
                    if existingAudio and existingAudio.strip() and os.path.exists(existingAudio):
                        completedLines += 1
                        processedLines += 1
                        updatedDialogue.append(updatedLine)
                        
                        # Call progress callback if provided
                        if progress_callback:
                            progress_percent = (processedLines / totalLines) * 100
                            progress_callback(progress_percent, f"Processed line {processedLines}/{totalLines} (existing audio)")
                        
                        continue
                    
                    if existingAudio and existingAudio.strip() and not os.path.exists(existingAudio):
                        updatedLine["audioFile"] = ""
                    
                    if speaker not in users:
                        failedLines += 1
                        processedLines += 1
                        updatedDialogue.append(updatedLine)
                        
                        # Call progress callback if provided
                        if progress_callback:
                            progress_percent = (processedLines / totalLines) * 100
                            progress_callback(progress_percent, f"Processed line {processedLines}/{totalLines} (character not found)")
                        
                        continue
                    
                    charData = users[speaker]
                    charAudioFile = charData.get("audioFile", "")
                    
                    if not charAudioFile or not os.path.exists(charAudioFile):
                        failedLines += 1
                        processedLines += 1
                        updatedDialogue.append(updatedLine)
                        
                        # Call progress callback if provided
                        if progress_callback:
                            progress_percent = (processedLines / totalLines) * 100
                            progress_callback(progress_percent, f"Processed line {processedLines}/{totalLines} (missing audio file)")
                        
                        continue
                    
                    charConfig = charData.get("config", {})
                    
                    outputFilename = generateAudioFilename(scriptId, lineIndex, speaker)
                    outputPath = os.path.join(generatedAudioDir, outputFilename)
                    
                    try:
                        tempAudioPath = f5ttsClient.generateSpeech(charAudioFile, text, charConfig)
                        
                        if tempAudioPath and os.path.exists(tempAudioPath):
                            try:
                                shutil.copy2(tempAudioPath, outputPath)
                                
                                if os.path.exists(outputPath) and os.path.getsize(outputPath) > 0:
                                    updatedLine["audioFile"] = outputPath
                                    completedLines += 1
                                else:
                                    if os.path.exists(outputPath):
                                        try:
                                            os.remove(outputPath)
                                        except:
                                            pass
                                    failedLines += 1
                            except Exception:
                                failedLines += 1
                        else:
                            failedLines += 1
                            
                    except Exception:
                        failedLines += 1
                    
                    processedLines += 1
                    updatedDialogue.append(updatedLine)
                    
                    # Call progress callback if provided
                    if progress_callback:
                        progress_percent = (processedLines / totalLines) * 100
                        progress_callback(progress_percent, f"Generated audio for line {processedLines}/{totalLines}")
                    
                except Exception:
                    failedLines += 1
                    processedLines += 1
                    updatedDialogue.append({
                        "speaker": dialogueLine.get("speaker", ""),
                        "text": dialogueLine.get("text", ""),
                        "audioFile": ""
                    })
                    
                    # Call progress callback if provided
                    if progress_callback:
                        progress_percent = (processedLines / totalLines) * 100
                        progress_callback(progress_percent, f"Processed line {processedLines}/{totalLines} (failed)")
                    
                    continue
            
            script["dialogue"] = updatedDialogue
            script["updatedAt"] = datetime.now().isoformat()
            scripts[scriptId] = script
            
            if completedLines == totalLines:
                status = "completed"
                message = f"✅ Successfully generated audio for all {completedLines} dialogue lines"
            elif completedLines > 0:
                status = "partial"
                message = f"⚠️ Generated audio for {completedLines}/{totalLines} lines ({failedLines} failed)"
            else:
                status = "failed"
                message = f"❌ Failed to generate audio for any lines ({failedLines} failures)"
            
            print(f"🎯 Audio generation completed: {message}")
            
            return AudioGenerationResponse(
                scriptId=scriptId,
                status=status,
                message=message,
                completedLines=completedLines,
                totalLines=totalLines
            )
            
        finally:
            f5ttsClient.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in audio generation for script {scriptId}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Audio generation failed: {str(e)}") 