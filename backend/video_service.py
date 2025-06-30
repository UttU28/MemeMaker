import os
import random
import subprocess
import traceback
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from fastapi import HTTPException
from pydub import AudioSegment
import re
from models import VideoGenerationResponse

logger = logging.getLogger(__name__)

class VideoGenerator:
    def __init__(self):
        print("🎬 VideoGenerator initialized")
        
    def _getRandomBackgroundVideo(self, backgroundDir: str, defaultBackgroundVideo: str) -> str:
        try:
            if os.path.exists(backgroundDir):
                backgroundFiles = [f for f in os.listdir(backgroundDir) 
                                 if f.startswith('background') and f.endswith('.mp4')]
                if backgroundFiles:
                    randomBackground = random.choice(backgroundFiles)
                    backgroundVideo = os.path.join(backgroundDir, randomBackground)
                    print(f"🎲 Selected background: {randomBackground}")
                    return backgroundVideo
            
            if os.path.exists(defaultBackgroundVideo):
                print(f"📺 Using default background: {defaultBackgroundVideo}")
                return defaultBackgroundVideo
            else:
                raise Exception(f"No background video found: {defaultBackgroundVideo}")
                
        except Exception as e:
            logger.error(f"❌ Background video error: {str(e)}")
            raise Exception(f"Background video error: {str(e)}")
    
    def _generateSubtitleForAudio(self, audioFile: str, dialogueText: str) -> Optional[Dict]:
        try:
            if not audioFile or not dialogueText:
                return None
            
            if not os.path.exists(audioFile):
                return None
            
            try:
                audio = AudioSegment.from_file(audioFile)
                audioDuration = len(audio) / 1000.0
            except Exception as e:
                return None
            
            return self._generateSimpleSubtitles(dialogueText, audioDuration)
            
        except Exception as e:
            try:
                if 'audioDuration' not in locals():
                    audio = AudioSegment.from_file(audioFile)
                    audioDuration = len(audio) / 1000.0
            except:
                audioDuration = 3.0
            return self._generateSimpleSubtitles(dialogueText, audioDuration)

    def _generateSimpleSubtitles(self, dialogueText: str, audioDuration: float) -> Dict:
        try:
            cleanText = re.sub(r'[^\w\s]', '', dialogueText.strip())
            words = cleanText.split()
            
            if not words:
                return {"segments": [], "duration": audioDuration}
            
            segments = []
            wordsPerSegment = 4
            
            for i in range(0, len(words), wordsPerSegment):
                segmentWords = words[i:i + wordsPerSegment]
                segmentText = " ".join(segmentWords)
                
                segmentStart = (i / len(words)) * audioDuration
                segmentEnd = min(((i + len(segmentWords)) / len(words)) * audioDuration, audioDuration)
                
                if segmentEnd - segmentStart < 0.5:
                    segmentEnd = min(segmentStart + 0.5, audioDuration)
                
                segments.append({
                    "start": round(segmentStart, 3),
                    "end": round(segmentEnd, 3),
                    "text": segmentText
                })
            
            return {
                "segments": segments,
                "duration": audioDuration
            }
            
        except Exception as e:
            return {"segments": [], "duration": audioDuration}
    
    def _createTimeline(self, scriptData: Dict, userProfiles: Dict) -> Tuple[List[Dict], float]:
        try:
            dialogueLines = scriptData.get("dialogue", [])
            if not dialogueLines:
                return [], 0
            
            timeline = []
            currentTime = 0
            skippedCount = 0
            
            print(f"🎬 Creating timeline: {len(dialogueLines)} lines")
            
            for i, dialogueLine in enumerate(dialogueLines):
                try:
                    speaker = dialogueLine.get("speaker", "").lower()
                    text = dialogueLine.get("text", "")
                    audioFile = dialogueLine.get("audioFile", "")
                    
                    if not audioFile or not text or not speaker:
                        skippedCount += 1
                        continue
                    
                    if not os.path.exists(audioFile):
                        skippedCount += 1
                        continue
                    
                    subtitleInfo = self._generateSubtitleForAudio(audioFile, text)
                    if not subtitleInfo:
                        skippedCount += 1
                        continue
                    
                    characterImage = self._getCharacterImage(speaker, userProfiles)
                    
                    timelineItem = {
                        "lineIndex": i,
                        "speaker": speaker,
                        "text": text,
                        "audioFile": audioFile,
                        "imageFile": characterImage,
                        "startTime": currentTime,
                        "endTime": currentTime + subtitleInfo["duration"],
                        "duration": subtitleInfo["duration"],
                        "subtitleSegments": subtitleInfo["segments"]
                    }
                    
                    timeline.append(timelineItem)
                    currentTime += subtitleInfo["duration"]
                    
                except Exception as e:
                    skippedCount += 1
                    continue
            
            if not timeline:
                return [], 0
            
            print(f"✅ Timeline: {len(timeline)} items, {currentTime:.2f}s (skipped {skippedCount})")
            return timeline, currentTime
            
        except Exception as e:
            return [], 0
    
    def _getCharacterImage(self, speaker: str, userProfiles: Dict) -> str:
        try:
            users = userProfiles.get("users", {})
            if speaker not in users:
                return ""
            
            characterData = users[speaker]
            images = characterData.get("images", {})
            
            if not images:
                return ""
            
            imagePaths = list(images.values())
            randomImage = random.choice(imagePaths)
            
            if os.path.exists(randomImage):
                return randomImage
            else:
                return ""
                
        except Exception as e:
            return ""
    
    def _concatenateAudioFiles(self, timeline: List[Dict], outputPath: str) -> bool:
        try:
            if not timeline:
                return False
            
            print(f"🎵 Concatenating {len(timeline)} audio files...")
            
            combinedAudio = AudioSegment.empty()
            processedCount = 0
            
            for i, item in enumerate(timeline):
                try:
                    audioFile = item.get("audioFile", "")
                    if not audioFile or not os.path.exists(audioFile):
                        continue
                    
                    audio = AudioSegment.from_file(audioFile)
                    
                    if len(audio) == 0:
                        continue
                    
                    combinedAudio += audio
                    processedCount += 1
                    
                except Exception:
                    continue
            
            if processedCount == 0:
                return False
            
            try:
                os.makedirs(os.path.dirname(outputPath), exist_ok=True)
                combinedAudio.export(outputPath, format="wav")
                
                if not os.path.exists(outputPath) or os.path.getsize(outputPath) == 0:
                    return False
                
                print(f"✅ Audio concatenation successful: {processedCount} files, duration: {len(combinedAudio)/1000:.2f}s")
                return True
                
            except Exception:
                return False
            
        except Exception:
            return False
    
    def _getVideoDuration(self, videoPath: str) -> float:
        try:
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', videoPath
            ], capture_output=True, text=True, timeout=10)
            return float(result.stdout.strip()) if result.returncode == 0 else 3.0
        except Exception:
            return 3.0
    
    def _generateVideoWithFfmpeg(self, backgroundVideo: str, timeline: List[Dict],
                                totalDuration: float, combinedAudio: str, 
                                outputVideo: str, scriptId: str, fontPath: str) -> Tuple[bool, Optional[int]]:
        try:
            print(f"🎬 Generating video with FFmpeg")
            print(f"📹 Background: {backgroundVideo}")
            print(f"🎵 Audio: {combinedAudio}")
            print(f"⏱️ Duration: {totalDuration:.2f}s")
            print(f"📤 Output: {outputVideo}")
            
            os.makedirs(os.path.dirname(outputVideo), exist_ok=True)
            
            if not os.path.exists(fontPath):
                fontPath = 'arial'
            else:
                fontPath = fontPath.replace(':', '\\:')
            
            filterParts = []
            inputParts = ['-hwaccel', 'cuda', '-stream_loop', '-1', '-i', backgroundVideo, '-i', combinedAudio]
            
            imageInputs = {}
            validImages = 0
            inputIndex = 2
            
            for item in timeline:
                imageFile = item.get("imageFile", "")
                if imageFile and os.path.exists(imageFile):
                    inputParts.extend(['-i', imageFile])
                    imageInputs[item["lineIndex"]] = inputIndex
                    inputIndex += 1
                    validImages += 1
            
            print(f"🖼️ Added {validImages}/{len(timeline)} images")
            
            try:
                filterParts.append(f"[0:v]scale=1080:1920:force_original_aspect_ratio=disable,setsar=1,trim=duration={totalDuration},setpts=PTS-STARTPTS[bg]")
                currentBase = "[bg]"
                
                overlayCount = 0
                subtitleCount = 0
                
                for item in timeline:
                    lineIndex = item.get("lineIndex", 0)
                    
                    if lineIndex in imageInputs:
                        imgInput = imageInputs[lineIndex]
                        filterParts.append(
                            f"{currentBase}[{imgInput}:v]overlay=0:0:enable='between(t,{item['startTime']},{item['endTime']})'[overlay{overlayCount}]"
                        )
                        currentBase = f"[overlay{overlayCount}]"
                        overlayCount += 1
                    
                    if "subtitleSegments" in item and item["subtitleSegments"]:
                        for segment in item["subtitleSegments"]:
                            start = item["startTime"] + segment["start"]
                            end = item["startTime"] + segment["end"]
                            text = segment.get("text", "").strip()
                            
                            if not text:
                                continue
                                
                            text = text.replace("'", "\\'").replace('"', '\\"').replace(':', '\\:')
                            
                            filterParts.append(
                                f"{currentBase}drawtext=text='{text}':fontfile='{fontPath}':fontsize=64:borderw=3:bordercolor=black:fontcolor=white:x=(w-text_w)/2:y=h-th-150:enable='between(t,{start:.3f},{end:.3f})'[sub{subtitleCount}]"
                            )
                            currentBase = f"[sub{subtitleCount}]"
                            subtitleCount += 1
                
                print(f"🎭 Added {overlayCount} overlays, {subtitleCount} subtitles")
                
                filterParts.append(f"{currentBase}setpts=PTS-STARTPTS[final_video]")
                outputMapping = ['-map', '[final_video]', '-map', '1:a']
                
            except Exception:
                return (False, None)
            
            try:
                filterComplex = ";".join(filterParts)
                
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
                
                print("⚡ Executing FFmpeg...")
                
            except Exception:
                return (False, None)
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                
                if result.returncode != 0:
                    return (False, None)
                
                if not os.path.exists(outputVideo) or os.path.getsize(outputVideo) == 0:
                    return (False, None)
                
                fileSize = os.path.getsize(outputVideo)
                print(f"✅ Video generation successful!")
                print(f"📤 Output: {outputVideo}")
                print(f"📊 Size: {fileSize} bytes")
                
                return (True, fileSize)
                
            except subprocess.TimeoutExpired:
                return (False, None)
            except Exception:
                return (False, None)
                
        except Exception:
            return (False, None)
    
    async def generateVideo(self, scriptId: str, scriptsData: Dict, userProfiles: Dict,
                           videoOutputDir: str, backgroundDir: str, defaultBackgroundVideo: str,
                           fontPath: str, backgroundVideo: Optional[str] = None) -> VideoGenerationResponse:
        try:
            print(f"🎬 Starting video generation for script: {scriptId}")
            
            scripts = scriptsData.get("scripts", {})
            
            if scriptId not in scripts:
                raise HTTPException(status_code=404, detail=f"Script '{scriptId}' not found")
            
            scriptData = scripts[scriptId]
            dialogueLines = scriptData.get("dialogue", [])
            
            if not dialogueLines:
                raise HTTPException(status_code=400, detail="Script has no dialogue lines")
            
            missingAudio = []
            for i, line in enumerate(dialogueLines):
                audioFile = line.get("audioFile", "")
                if not audioFile or not os.path.exists(audioFile):
                    missingAudio.append(i)
            
            if missingAudio:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Audio files missing for dialogue lines: {missingAudio}. Generate audio first."
                )
            
            if not backgroundVideo:
                backgroundVideo = self._getRandomBackgroundVideo(backgroundDir, defaultBackgroundVideo)
            
            if not os.path.exists(backgroundVideo):
                raise HTTPException(status_code=400, detail=f"Background video not found: {backgroundVideo}")
            
            print("🎬 Creating timeline...")
            timeline, totalDuration = self._createTimeline(scriptData, userProfiles)
            
            if not timeline:
                raise HTTPException(status_code=500, detail="Failed to create timeline - no valid segments")
            
            print(f"Created timeline with {len(timeline)} segments, total duration: {totalDuration:.2f}s")
            
            print("🎵 Concatenating audio files...")
            combinedAudioPath = os.path.join(videoOutputDir, f"{scriptId}_combined_audio.wav")
            
            if not self._concatenateAudioFiles(timeline, combinedAudioPath):
                raise HTTPException(status_code=500, detail="Failed to concatenate audio files")
            
            print("🎬 Generating final video...")
            finalVideoPath = os.path.join(videoOutputDir, f"{scriptId}_final_video.mp4")
            
            success, videoSize = self._generateVideoWithFfmpeg(
                backgroundVideo, timeline, totalDuration, combinedAudioPath, finalVideoPath, scriptId, fontPath
            )
            
            if not success:
                raise HTTPException(status_code=500, detail="FFmpeg video generation failed")
            
            scriptData["finalVideoPath"] = finalVideoPath
            scriptData["videoDuration"] = totalDuration
            scriptData["videoSize"] = videoSize
            scriptData["updatedAt"] = datetime.now().isoformat()
            scripts[scriptId] = scriptData
            
            try:
                if os.path.exists(combinedAudioPath):
                    os.remove(combinedAudioPath)
                    print(f"🗑️ Cleaned up temp file")
            except Exception:
                pass
            
            print(f"✅ Video generation completed: {scriptId}")
            
            return VideoGenerationResponse(
                scriptId=scriptId,
                status="completed",
                message=f"✅ Video generated with {len(timeline)} segments",
                finalVideoPath=finalVideoPath,
                duration=totalDuration,
                videoSize=videoSize
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Video generation failed: {scriptId} - {str(e)}")
            raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}") 