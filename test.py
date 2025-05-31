import json
import os
import whisperx
import torch
import subprocess
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

def readWordData():
    try:
        with open('data/wordData.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading word data: {e}")
        return None

def getDialoguesForWord(word, data):
    if not data or 'words' not in data or word not in data['words']:
        return None
    
    wordData = data['words'][word]
    if 'chats' not in wordData:
        return None
    
    dialogues = []
    sortedChatKeys = sorted(wordData['chats'].keys(), key=lambda x: int(x.replace('chat', '')))
    
    for chatKey in sortedChatKeys:
        chat = wordData['chats'][chatKey]
        if 'dialogue' in chat:
            dialogues.append(chat['dialogue'])
    
    return "\n".join(dialogues)

def extractAudioWithFfmpeg(videoPath, audioPath):
    command = ["ffmpeg", "-y", "-i", videoPath, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", audioPath]
    try:
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print(f"FFmpeg audio extraction error: {result.stderr}")
        return result.returncode == 0
    except FileNotFoundError:
        print("Error: FFmpeg not found.")
        return False

def formatTime(seconds):
    millis = int((seconds - int(seconds)) * 1000)
    seconds = int(seconds)
    mins, secs = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)
    return f"{hours:02}:{mins:02}:{secs:02},{millis:03}"

def createSubtitlesForVideo(extractedText, videoPath, outputVideoPath, inputWord):
    device = "cpu"
    audioPath = "temp_audio.wav"
    srtPath = "subtitles.srt"
    
    print(f"Processing: {inputWord.upper()}")

    if not os.path.exists(audioPath):
        print("Extracting audio...")
        if not extractAudioWithFfmpeg(videoPath, audioPath):
            return False

    try:
        print("Loading models and transcribing...")
        whisperModel = whisperx.load_model("base", device, compute_type="float32")
        transcription = whisperModel.transcribe(audioPath, batch_size=1)

        if not transcription.get("segments"):
            print("No speech detected!")
            return False

        alignModel, metadata = whisperx.load_align_model(language_code="en", device=device)
        alignedData = whisperx.align(transcription["segments"], alignModel, metadata, audioPath, device)

        if not alignedData.get("word_segments"):
            print("Word alignment failed!")
            return False

        print("Generating subtitles...")
        with open(srtPath, 'w', encoding='utf-8') as srtFile:
            wordSegments = alignedData["word_segments"]
            groupSize = 4
            groupIndex = 1
            
            for i in range(0, len(wordSegments), groupSize):
                group = wordSegments[i:i+groupSize]
                start = group[0]['start']
                end = group[-1]['end']
                text = ""
                
                for word in group:
                    wordText = word['word'].strip()
                    if wordText:
                        text += f"<font face='Impact' size='16' color='&HFFFFFF&'>{wordText}</font> "
                
                srtFile.write(f"{groupIndex}\n{formatTime(start)} --> {formatTime(end)}\n{text.strip()}\n\n")
                groupIndex += 1

        print("Creating final video...")
        subtitleStyle = "FontName=Impact,FontSize=16,PrimaryColour=&HFFFFFF&,BorderStyle=1,Outline=3,BackColour=&H80000000&,Bold=1,MarginV=60"
        mainWord = inputWord.upper()
        
        videoFilter = f"subtitles={srtPath}:force_style='{subtitleStyle}',drawtext=text='Todays Word!':fontfile='C\\:/Windows/Fonts/impact.ttf':fontsize=60:fontcolor=white:borderw=3:bordercolor=black:shadowx=2:shadowy=2:shadowcolor=black:x=(w-text_w)/2:y=80,drawtext=text='{mainWord}':fontfile='C\\:/Windows/Fonts/impact.ttf':fontsize=140:fontcolor=yellow:borderw=6:bordercolor=black:shadowx=3:shadowy=3:shadowcolor=black:x=(w-text_w)/2:y=140"
        
        result = subprocess.run([
            "ffmpeg", "-y", "-hwaccel", "cuda", "-i", videoPath, "-vf", videoFilter, "-c:v", "h264_nvenc", "-preset", "fast", outputVideoPath
        ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            print(f"Video creation error: {result.stderr}")
            return False

        for file in [audioPath, srtPath]:
            if os.path.exists(file):
                os.remove(file)

        print(f"✅ Video saved: {outputVideoPath}")
        return True

    except Exception as e:
        print(f"Processing error: {e}")
        if os.path.exists(audioPath):
            os.remove(audioPath)
        return False

def main():
    data = readWordData()
    if not data:
        return

    inputWord = "defy"
    dialogues = getDialoguesForWord(inputWord, data)

    if dialogues:
        print(f"\nDialogues for '{inputWord}':")
        print(dialogues)
        
        videoPath = "C:/Users/utsav/OneDrive/Desktop/VoiceClonning_F5-TTS/data/video_output/defy_dialogue_video.mp4"
        if not os.path.exists(videoPath):
            print(f"Error: Video file not found!")
            return

        outputVideoPath = "output_with_subtitles.mp4"
        success = createSubtitlesForVideo(dialogues, videoPath, outputVideoPath, inputWord)
        
        if not success:
            print("Failed to create subtitles.")
    else:
        print(f"Word '{inputWord}' not found.")
        if data and 'words' in data:
            availableWords = list(data['words'].keys())
            print(f"Available: {', '.join(availableWords)}")

if __name__ == "__main__":
    main()