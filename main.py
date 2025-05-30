import json
import subprocess
import os
import sys
import requests
from dotenv import load_dotenv
from prompts import CHAT_GENERATION_PROMPT, GET_THE_MOOD_PROMPT
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

def detectMoodForDialogue(sentence: str, speaker: str):
    llmService = LlmService()
    
    if not llmService.isOllamaRunning():
        print("❌ Ollama not running - skipping mood detection")
        return None, None
        
    with open("data/userProfiles.json", "r") as f:
        profiles = json.load(f)
        if speaker in profiles["users"]:
            expressions = list(profiles["users"][speaker]["emotions"].keys())
            emotions = profiles["users"][speaker]["emotions"]
        else:
            expressions = ["confident"]
            emotions = {"confident": ""}
    
    options = ", ".join(expressions)
    prompt = GET_THE_MOOD_PROMPT.format(sentence=sentence, options=options)
    response = llmService.generate(prompt, provider="ollama", model="llama3.2")
    
    if response and response.strip().lower() in [exp.lower() for exp in expressions]:
        response = response.strip().lower()
    else:
        response = expressions[0]

    return response, emotions[response]

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


def isGradioRunning():
    try:
        response = requests.get("http://localhost:7860/")
        return response.status_code == 200
    except Exception as e:
        return False

def initializeWordData(word: str):
    """Initialize word data in JSON file"""
    jsonFileName = "data/wordData.json"
    
    try:
        if os.path.exists(jsonFileName):
            with open(jsonFileName, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"words": {}}
        
        data["words"][word.lower()] = {
            "word": word.lower(),
            "chats": {}
        }
        
        with open(jsonFileName, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Initialized data for word: {word}")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing word data: {e}")
        return False

def saveDialogueToJson(word: str, chatId: str, dialogue: str, speaker: str):
    """Save dialogue and speaker to JSON immediately"""
    jsonFileName = "data/wordData.json"
    
    try:
        with open(jsonFileName, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if word.lower() not in data["words"]:
            data["words"][word.lower()] = {"word": word.lower(), "chats": {}}
        
        data["words"][word.lower()]["chats"][chatId] = {
            "dialogue": dialogue,
            "speaker": speaker.lower()
        }
        
        with open(jsonFileName, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Saved dialogue for {chatId}: {speaker}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving dialogue: {e}")
        return False

def updateAudioFileInJson(word: str, chatId: str, audioFile: str):
    """Update audio file path in JSON"""
    jsonFileName = "data/wordData.json"
    
    try:
        with open(jsonFileName, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if word.lower() in data["words"] and chatId in data["words"][word.lower()]["chats"]:
            data["words"][word.lower()]["chats"][chatId]["audioFile"] = audioFile
            
            with open(jsonFileName, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Updated audio file for {chatId}")
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error updating audio file: {e}")
        return False

def updateImageFileInJson(word: str, chatId: str, imageFile: str):
    """Update image file path in JSON"""
    jsonFileName = "data/wordData.json"
    
    try:
        with open(jsonFileName, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if word.lower() in data["words"] and chatId in data["words"][word.lower()]["chats"]:
            data["words"][word.lower()]["chats"][chatId]["imageFile"] = imageFile
            
            with open(jsonFileName, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Updated image file for {chatId}")
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error updating image file: {e}")
        return False

def saveAllDialoguesToJson(word: str, dialogues: list):
    """Save all dialogues to JSON at once"""
    jsonFileName = "data/wordData.json"
    
    try:
        if os.path.exists(jsonFileName):
            with open(jsonFileName, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"words": {}}
        
        chats = {}
        for i, (dialogue, speaker) in enumerate(dialogues, 1):
            chats[f"chat{i}"] = {
                "dialogue": dialogue,
                "speaker": speaker.lower()
            }
        
        data["words"][word.lower()] = {
            "word": word.lower(),
            "chats": chats
        }
        
        with open(jsonFileName, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Saved {len(dialogues)} dialogues for '{word}'")
        return True
        
    except Exception as e:
        print(f"❌ Error saving dialogues: {e}")
        return False

def updateAllAudioFilesInJson(word: str, audioUpdates: dict):
    """Update all audio files in JSON at once"""
    jsonFileName = "data/wordData.json"
    
    try:
        with open(jsonFileName, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if word.lower() in data["words"]:
            for chatId, audioFile in audioUpdates.items():
                if chatId in data["words"][word.lower()]["chats"]:
                    data["words"][word.lower()]["chats"][chatId]["audioFile"] = audioFile
            
            with open(jsonFileName, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Updated {len(audioUpdates)} audio files")
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error updating audio files: {e}")
        return False

def updateAllImageFilesInJson(word: str, imageUpdates: dict):
    """Update all image files in JSON at once"""
    jsonFileName = "data/wordData.json"
    
    try:
        with open(jsonFileName, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if word.lower() in data["words"]:
            for chatId, imageFile in imageUpdates.items():
                if chatId in data["words"][word.lower()]["chats"]:
                    data["words"][word.lower()]["chats"][chatId]["imageFile"] = imageFile
            
            with open(jsonFileName, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Updated {len(imageUpdates)} image files")
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error updating image files: {e}")
        return False

def main():
    fullCleaning = len(sys.argv) > 1
    
    print("🎬 Voice Cloning Pipeline")
    print("=" * 30)

    # Check prerequisites
    if not isGradioRunning():
        print("❌ Gradio endpoint not running")
        return

    # Get word from user or command line
    if len(sys.argv) > 2:
        word = sys.argv[2]
    else:
        word = input("Enter word to process (default: Anomaly): ").strip() or "Anomaly"
    
    print(f"📝 Processing word: {word}")
    
    # Generate dialogue
    print("🤖 Generating dialogue...")
    dialogue = generateDialogue(word)
    
    if not dialogue:
        print("❌ Failed to generate dialogue")
        return
    
    print("✅ Dialogue generated:")
    print(dialogue)
    print()

    # Step 1: Parse and save all dialogues at once
    print("💾 Step 1: Parsing and saving all dialogues...")
    eachLine = dialogue.split("\n")
    dialogues = []
    dialogueDetails = []  # Keep for audio processing
    
    for line in eachLine:
        if line.strip() == "": 
            continue
            
        try:
            personName = line.split("}")[0].split("{")[1]
            lineText = line.split("}")[1].strip()
            userId = getUserId(personName)
            
            if userId:  # Only include if user exists
                dialogues.append((lineText, personName))
                dialogueDetails.append((lineText, personName, userId))
                print(f"  ✅ Parsed: {personName}")
        except Exception as e:
            print(f"  ⚠️ Error parsing line: {line[:30]}... - {e}")
            continue
    
    if not dialogues:
        print("❌ No valid dialogues parsed")
        return
    
    # Save all dialogues to JSON
    if not saveAllDialoguesToJson(word, dialogues):
        print("❌ Failed to save dialogues")
        return
    
    # Step 2: Generate audio for each chat individually
    print(f"\n🎵 Step 2: Generating audio for {len(dialogueDetails)} chats...")
    audioCount = 0
    
    for i, (lineText, personName, userId) in enumerate(dialogueDetails, 1):
        chatId = f"chat{i}"
        print(f"  🎙️ Generating audio for {chatId}: {personName}...")
        
        success, audioFileName = generateAudioForLine(userId, lineText)
        
        if success and audioFileName:
            # Clean audio
            cleanedFileName = cleanAudioFile(audioFileName, fullCleaning)
            
            if cleanedFileName:
                audioPath = f"audio_files/generated/{cleanedFileName}"
                # Update JSON immediately for this chat
                if updateAudioFileInJson(word, chatId, audioPath):
                    audioCount += 1
                    print(f"  ✅ Audio ready and saved: {chatId}")
                else:
                    print(f"  ❌ Failed to save audio path: {chatId}")
            else:
                print(f"  ❌ Audio cleaning failed: {chatId}")
        else:
            print(f"  ❌ Audio generation failed: {chatId}")
    
    # Step 3: Detect mood and assign images for each chat individually
    print(f"\n🎭 Step 3: Detecting moods for {len(dialogueDetails)} chats...")
    imageCount = 0
    
    for i, (lineText, personName, userId) in enumerate(dialogueDetails, 1):
        chatId = f"chat{i}"
        print(f"  🔍 Detecting mood for {chatId}: {personName}...")
        
        mood, imageFilePath = detectMoodForDialogue(lineText, personName.lower())
        
        if mood and imageFilePath:
            # Update JSON immediately for this chat
            if updateImageFileInJson(word, chatId, imageFilePath):
                imageCount += 1
                print(f"  ✅ Mood detected and saved: {chatId} - {mood}")
            else:
                print(f"  ❌ Failed to save image path: {chatId}")
        else:
            print(f"  ⚠️ No mood detected: {chatId}")
    
    print(f"\n🎉 Processing complete for '{word}'!")
    print(f"📊 Processed {len(dialogues)} dialogues")
    print(f"🎵 Generated {audioCount} audio files")
    print(f"🖼️ Assigned {imageCount} mood images")
    print("📁 All data saved to wordData.json")

if __name__ == "__main__":
    main()
