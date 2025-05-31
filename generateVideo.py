#!/usr/bin/env python3

import json
import os
import subprocess
import sys
from pathlib import Path
from pydub import AudioSegment

def loadWordData(word: str):
    """Load word data from JSON file"""
    try:
        with open("data/wordData.json", "r") as f:
            data = json.load(f)
            
        if word.lower() not in data["words"]:
            print(f"❌ Word '{word}' not found in wordData.json")
            availableWords = list(data["words"].keys())
            print(f"ℹ️ Available words: {availableWords}")
            return None
            
        return data["words"][word.lower()]
    except Exception as e:
        print(f"❌ Error loading word data: {e}")
        return None

def getAudioDuration(audioFile: str):
    """Get duration of audio file in seconds"""
    try:
        # Add data/ prefix if not already present
        if not audioFile.startswith('data/'):
            audioFile = 'data/' + audioFile
        audio = AudioSegment.from_file(audioFile)
        return len(audio) / 1000.0  # Convert ms to seconds
    except Exception as e:
        print(f"❌ Error getting audio duration: {e}")
        return 0

def createTimeline(wordData):
    """Create timeline with speaker positions and timing"""
    chats = wordData["chats"]
    timeline = []
    currentTime = 0
    
    for chatId in sorted(chats.keys(), key=lambda x: int(x.replace('chat', ''))):
        chatData = chats[chatId]
        audioFile = chatData["audioFile"]
        imageFile = chatData.get("imageFile", "")
        speaker = chatData["speaker"]
        dialogue = chatData["dialogue"]
        
        # Get audio duration
        duration = getAudioDuration(audioFile)
        if duration == 0:
            print(f"⚠️ Skipping {chatId} - invalid audio duration")
            continue
        
        timeline.append({
            "chatId": chatId,
            "speaker": speaker,
            "dialogue": dialogue,
            "audioFile": audioFile,
            "imageFile": imageFile,
            "startTime": currentTime,
            "endTime": currentTime + duration,
            "duration": duration
        })
        
        currentTime += duration
    
    return timeline, currentTime

def concatenateAudioFiles(timeline, outputPath: str):
    """Concatenate all audio files in sequence"""
    try:
        combinedAudio = AudioSegment.empty()
        
        for item in timeline:
            audioFile = item["audioFile"]
            # Add data/ prefix if not already present
            if not audioFile.startswith('data/'):
                audioFile = 'data/' + audioFile
            audio = AudioSegment.from_file(audioFile)
            combinedAudio += audio
        
        # Export combined audio
        os.makedirs(os.path.dirname(outputPath), exist_ok=True)
        combinedAudio.export(outputPath, format="wav")
        
        print(f"✅ Combined audio saved: {outputPath}")
        return True
        
    except Exception as e:
        print(f"❌ Error concatenating audio: {e}")
        return False

def generateVideoWithFFmpeg(backgroundVideo: str, timeline: list, totalDuration: float, 
                          combinedAudio: str, outputVideo: str):
    """Generate video using FFmpeg with complex filter chains and outro"""
    
    # Check if outro exists
    outroPath = "data/outro.mp4"
    useOutro = os.path.exists(outroPath)
    
    if useOutro:
        print(f"🎬 Adding outro: {outroPath}")
        # Get outro duration
        try:
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', 
                '-of', 'default=noprint_wrappers=1:nokey=1', outroPath
            ], capture_output=True, text=True)
            outroDuration = float(result.stdout.strip()) if result.returncode == 0 else 3.0
        except:
            outroDuration = 3.0
        print(f"📝 Outro duration: {outroDuration}s")
    else:
        outroDuration = 0
        print("⚠️ No outro.mp4 found in data directory")
    
    filterParts = []
    if useOutro:
        inputParts = ['-hwaccel', 'cuda', '-stream_loop', '-1', '-i', backgroundVideo, '-i', combinedAudio, '-i', outroPath]
        inputIndex = 3
    else:
        inputParts = ['-hwaccel', 'cuda', '-stream_loop', '-1', '-i', backgroundVideo, '-i', combinedAudio]
        inputIndex = 2
    
    imageInputs = {}

    for item in timeline:
        if item["imageFile"] and os.path.exists(item["imageFile"]):
            inputParts.extend(['-i', item["imageFile"]])
            imageInputs[item["chatId"]] = inputIndex
            inputIndex += 1

    # Debug: Show what images are being added as inputs
    print(f"🖼️ Adding {len(imageInputs)} images as inputs")
    for chatId, idx in imageInputs.items():
        print(f"  Input {idx}: {chatId}")

    # Create main video with overlays
    filterParts.append(f"[0:v]scale=1080:1920:force_original_aspect_ratio=disable,setsar=1,trim=duration={totalDuration},setpts=PTS-STARTPTS[bg]")
    currentBase = "[bg]"
    overlayIndex = 0

    for item in timeline:
        if item["chatId"] not in imageInputs:
            continue
            
        imgInput = imageInputs[item["chatId"]]
        startTime = item["startTime"]
        endTime = item["endTime"]
        
        overlayName = f"[overlay{overlayIndex}]"
        filterParts.append(
            f"{currentBase}[{imgInput}:v]overlay=0:0:enable='between(t,{startTime},{endTime})'{overlayName}"
        )
        
        currentBase = overlayName
        overlayIndex += 1

    if useOutro:
        # Scale outro to match main video dimensions and SAR
        filterParts.append(f"[2:v]scale=1080:1920:force_original_aspect_ratio=disable,setsar=1,setpts=PTS-STARTPTS[outro_scaled]")
        
        # Concatenate main video with outro
        filterParts.append(f"{currentBase}[outro_scaled]concat=n=2:v=1:a=0[final_video]")
        
        # Create silence for outro duration and concatenate with main audio
        filterParts.append(f"anullsrc=channel_layout=mono:sample_rate=24000[silence]")
        filterParts.append(f"[1:a][silence]concat=n=2:v=0:a=1[temp_audio]")
        filterParts.append(f"[temp_audio]atrim=duration={totalDuration + outroDuration}[final_audio]")
        
        outputMapping = ['-map', '[final_video]', '-map', '[final_audio]']
    else:
        filterParts.append(f"{currentBase}setpts=PTS-STARTPTS[final_video]")
        outputMapping = ['-map', '[final_video]', '-map', '1:a']

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

    print("🎬 Generating video with FFmpeg...")
    print(f"📝 Filter: {filterComplex}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ Video generated successfully: {outputVideo}")
            if useOutro:
                print(f"🎉 Outro added: +{outroDuration}s")
            return True
        else:
            print(f"❌ FFmpeg error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running FFmpeg: {e}")
        return False

def generateDialogueVideo(word: str, backgroundVideo: str = None):
    """Main function to generate dialogue video"""
    
    print(f"🎥 Generating dialogue video for word: {word}")
    print("=" * 50)
    
    # Load word data
    wordData = loadWordData(word)
    if not wordData:
        return False
    
    # Use fixed background video path
    if not backgroundVideo:
        backgroundVideo = r"downloads/Minecraft Parkour Gameplay No Copyright_mobile.mp4"
        
    if not os.path.exists(backgroundVideo):
        print(f"❌ Background video not found: {backgroundVideo}")
        return False
        
    print(f"📹 Using background video: {backgroundVideo}")
    
    # Create timeline
    timeline, totalDuration = createTimeline(wordData)
    if not timeline:
        print("❌ No valid timeline created")
        return False
    
    print(f"📊 Timeline created: {len(timeline)} segments, {totalDuration:.2f}s total")
    
    # Debug: Show what images are being processed
    for item in timeline:
        imageExists = os.path.exists(item['imageFile']) if item['imageFile'] else False
        print(f"  {item['chatId']}: {item['speaker']} - Audio: {item['duration']:.2f}s")
        print(f"    Image: {item['imageFile']} {'✅' if imageExists else '❌'}")
    
    # Create output directories
    os.makedirs("data/video_output", exist_ok=True)
    combinedAudioPath = f"data/video_output/{word}_combined_audio.wav"
    outputVideoPath = f"data/video_output/{word}_dialogue_video.mp4"
    
    # Concatenate audio files
    if not concatenateAudioFiles(timeline, combinedAudioPath):
        return False
    
    # Generate video
    success = generateVideoWithFFmpeg(
        backgroundVideo, timeline, totalDuration, 
        combinedAudioPath, outputVideoPath
    )
    
    if success:
        print("🎉 Video generation complete!")
        print(f"📁 Output: {outputVideoPath}")
        
        # Clean up temporary audio file
        if os.path.exists(combinedAudioPath):
            os.remove(combinedAudioPath)
            print("🧹 Temporary files cleaned")
        
        return True
    else:
        return False

def main():
    if len(sys.argv) > 1:
        word = sys.argv[1]
    else:
        word = input("Enter word to generate video for: ").strip() or "defy"
    
    if len(sys.argv) > 2:
        backgroundVideo = sys.argv[2]
    else:
        backgroundVideo = None
    
    success = generateDialogueVideo(word, backgroundVideo)
    
    if success:
        print("✅ Process completed successfully!")
    else:
        print("❌ Process failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()