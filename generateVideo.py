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
    """Generate video using FFmpeg with complex filter chains"""
    
    filterParts = []
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

    filterParts.append(f"[0:v]scale=1080:1920,trim=duration={totalDuration},setpts=PTS-STARTPTS[bg]")
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

    filterParts.append(f"{currentBase}setpts=PTS-STARTPTS[out]")
    filterComplex = ";".join(filterParts)

    cmd = [
        'ffmpeg', '-y',
        *inputParts,
        '-filter_complex', filterComplex,
        '-map', '[out]',
        '-map', '1:a',
        '-c:v', 'h264_nvenc',
        '-preset', 'fast',
        '-c:a', 'aac',
        '-t', str(totalDuration),
        '-shortest',
        outputVideo
    ]

    print("🎬 Generating video with FFmpeg...")
    print(f"📝 Filter: {filterComplex}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ Video generated successfully: {outputVideo}")
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