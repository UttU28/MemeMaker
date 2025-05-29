import json
import subprocess
import os
import sys
import requests
from dotenv import load_dotenv
from prompts import CHAT_GENERATION_PROMPT
from pydub import AudioSegment, silence
from src.client import F5TtsGradioClient
from src.config import ConfigManager
from src.utils import AudioFileManager
from src.llm import LlmService

load_dotenv()

def generateDialogue(word):
    llmService = LlmService()
    formattedPrompt = CHAT_GENERATION_PROMPT.format(word=word.capitalize())
    
    dialogue = llmService.generate(formattedPrompt, provider="openai")
    if dialogue:
        return llmService.cleanResponse(dialogue)
    
    return None

thisConvo = """
{Rahul} I heard someone say my popularity *plummeted*. What does that even mean?

{Modi} It means to fall very fast, Rahul. Like how your party drops after every election result.

{Rahul} Hey, that's rude! I was just asking.

{Shashi} "Plummet" is a verb. It means to drop suddenly and steeply. For example, stock prices can plummet... or public opinion can plummet — especially after a confusing speech.

{Rahul} So basically, it's a fancy word for falling really fast?

{Modi} Yes. Very fast. Like petrol prices... in our dreams.

{Shashi} Or like attention spans — when someone talks for too long without making a point.
"""

def getUserId(personName: str):
    with open("data/userProfiles.json", "r") as f:
        data = json.load(f)
        for userId, userData in data["users"].items():
            if userData["displayName"].lower() == personName.lower():
                return userId
    return None

def generateAudioForLine(userId: str, lineText: str):
    if not userId:
        return False, None
    
    configManager = ConfigManager()
    if not configManager.validateUserProfile(userId):
        return False, None
    
    client = F5TtsGradioClient()
    
    try:
        if not client.connectToGradio():
            return False, None
        
        success = client.generateSpeechWithUser(userId, lineText)
        
        if success:
            audioManager = AudioFileManager()
            outputPrefix = configManager.getOutputPrefixWithFallback(userId)
            generatedFiles = audioManager.listGeneratedFiles(outputPrefix)
            if generatedFiles:
                return True, generatedFiles[0]
            return True, None
        else:
            return False, None
                    
    except Exception as e:
        return False, None
    finally:
        client.close()

def cleanAudioFile(audioFileName: str, fullCleaning: bool = False):
    audioManager = AudioFileManager()
    inputPath = audioManager.getGeneratedFilePath(audioFileName)
    
    if not os.path.exists(inputPath):
        return None
    
    try:
        audio = AudioSegment.from_file(inputPath)
        
        if fullCleaning:
            silenceThreshDb = -40
            minSilenceLenMs = 250
            paddingMs = 75
            
            chunks = silence.detect_nonsilent(audio,
                                             min_silence_len=minSilenceLenMs,
                                             silence_thresh=silenceThreshDb)
            
            if not chunks:
                return None
            
            cleanedAudio = AudioSegment.empty()
            for start, end in chunks:
                cleanedAudio += audio[start:end]
                cleanedAudio += AudioSegment.silent(duration=paddingMs)
        else:
            silenceThreshDb = -40
            minSilenceLenMs = 100
            
            chunks = silence.detect_nonsilent(audio,
                                             min_silence_len=minSilenceLenMs,
                                             silence_thresh=silenceThreshDb)
            
            if not chunks:
                return None
            
            startTrim = chunks[0][0]
            endTrim = chunks[-1][1]
            
            paddingMs = 50
            startTrim = max(0, startTrim - paddingMs)
            endTrim = min(len(audio), endTrim + paddingMs)
            
            cleanedAudio = audio[startTrim:endTrim]
        
        baseName = os.path.splitext(audioFileName)[0]
        modeSuffix = "full_cleaned" if fullCleaning else "trimmed"
        cleanedFileName = f"{modeSuffix}_{baseName}.wav"
        outputPath = audioManager.getGeneratedFilePath(cleanedFileName)
        cleanedAudio.export(outputPath, format="wav")
        
        return cleanedFileName
        
    except Exception as e:
        return None

def saveWordData(word: str, dialogueData: list, cleanedAudioFiles: list):
    jsonFileName = "data/wordData.json"
    
    try:
        if os.path.exists(jsonFileName):
            with open(jsonFileName, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"words": {}}
        
        chats = {}
        for i, (dialogue, speaker, audioFileName) in enumerate(dialogueData, 1):
            if i <= len(cleanedAudioFiles):
                chats[f"chat{i}"] = {
                    "dialogue": dialogue,
                    "speaker": speaker.lower(),
                    "audioFile": f"data/audio_files/generated/{cleanedAudioFiles[i-1]}"
                }
        
        data["words"][word.lower()] = {
            "word": word.lower(),
            "chats": chats
        }
        
        with open(jsonFileName, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        return jsonFileName
        
    except Exception as e:
        print(f"Error saving word data: {e}")
        return None

def updateWordDataWithFinalAudio(word: str, finalAudioPath: str):
    jsonFileName = "data/wordData.json"
    
    try:
        if os.path.exists(jsonFileName):
            with open(jsonFileName, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if word.lower() in data.get("words", {}):
                data["words"][word.lower()]["finalAudioFile"] = finalAudioPath
                
                with open(jsonFileName, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                
                return True
        
        return False
        
    except Exception as e:
        print(f"Error updating final audio: {e}")
        return False

def mergeAudioFiles(audioFileNames: list, outputFileName: str = "conversation_merged.wav"):
    if not audioFileNames:
        return False
    
    audioManager = AudioFileManager()
    fileListPath = "temp_file_list.txt"
    
    try:
        with open(fileListPath, 'w') as f:
            for i, audioFileName in enumerate(audioFileNames):
                audioPath = audioManager.getGeneratedFilePath(audioFileName)
                if audioFileName and os.path.exists(audioPath):
                    f.write(f"file '{audioPath}'\n")
                    if i < len(audioFileNames) - 1:
                        f.write(f"file 'silence.wav'\n")
        
        silenceCmd = [
            "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=22050:cl=mono", 
            "-t", "0.5", "silence.wav"
        ]
        subprocess.run(silenceCmd, capture_output=True)
        
        ffmpegCmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", fileListPath,
            "-c", "copy", outputFileName
        ]
        
        result = subprocess.run(ffmpegCmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Merged: {outputFileName}")
            return True
        else:
            return False
            
    except Exception as e:
        return False
    finally:
        if os.path.exists(fileListPath):
            os.remove(fileListPath)
        if os.path.exists("silence.wav"):
            os.remove("silence.wav")

def isGradioRunning():
    try:
        response = requests.get("http://localhost:7860/")
        return response.status_code == 200
    except Exception as e:
        return False

def main():
    fullCleaning = len(sys.argv) > 1

    if not isGradioRunning():
        print("Gradio endpoint not running")
        return

    word = "Anomaly"
    dialogue = generateDialogue(word)
    
    if not dialogue:
        print("Failed to generate dialogue")
        return
    
    print(dialogue)

    eachLine = dialogue.split("\n")
    generatedAudioFiles = []
    dialogueData = []
    
    for line in eachLine:
        if line.strip() == "": 
            continue
            
        try:
            personName = line.split("}")[0].split("{")[1]
            lineText = line.split("}")[1].strip()
            userId = getUserId(personName)
            
            if userId:
                success, audioFileName = generateAudioForLine(userId, lineText)
                if success and audioFileName:
                    generatedAudioFiles.append(audioFileName)
                    dialogueData.append((lineText, personName, audioFileName))
        except Exception as e:
            continue
    
    if not generatedAudioFiles:
        print("No audio files generated")
        return
    
    cleanedAudioFiles = []
    for audioFileName in generatedAudioFiles:
        cleanedFileName = cleanAudioFile(audioFileName, fullCleaning)
        if cleanedFileName:
            cleanedAudioFiles.append(cleanedFileName)
    
    if cleanedAudioFiles:
        saveWordData(word, dialogueData, cleanedAudioFiles)
        
        finalAudioPath = f"data/audio_files/merged/{word.lower()}_conversation.wav"
        os.makedirs("data/audio_files/merged", exist_ok=True)
        
        success = mergeAudioFiles(cleanedAudioFiles, finalAudioPath)
        if success:
            updateWordDataWithFinalAudio(word, finalAudioPath)

if __name__ == "__main__":
    main()
