#!/usr/bin/env python3

import json
from src.llm import LlmService
from prompts import GET_THE_MOOD_PROMPT

def testOllamaMood(sentence: str, speaker: str):
    llmService = LlmService()
    
    if not llmService.isOllamaRunning():
        print("❌ Ollama not running")
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

def processWordData(word: str):
    try:
        with open("data/wordData.json", "r") as f:
            wordData = json.load(f)
    except FileNotFoundError:
        print("❌ wordData.json not found!")
        return
    except json.JSONDecodeError:
        print("❌ Error reading wordData.json!")
        return
    
    if word not in wordData["words"]:
        print(f"❌ Word '{word}' not found")
        availableWords = list(wordData["words"].keys())
        print(f"Available words: {availableWords}")
        return
    
    chats = wordData["words"][word]["chats"]
    print(f"Processing '{word}' - {len(chats)} chats")
    
    for chatId, chatData in chats.items():
        dialogue = chatData["dialogue"]
        speaker = chatData["speaker"]
        
        if "imageFile" in chatData:
            print(f"⏩ {chatId}: {speaker} - Already processed")
            continue
        
        print(f"Processing {chatId}: {speaker}")
        
        mood, imageFilePath = testOllamaMood(dialogue, speaker)
        
        if mood and imageFilePath:
            wordData["words"][word]["chats"][chatId]["imageFile"] = imageFilePath
            
            try:
                with open("data/wordData.json", "w") as f:
                    json.dump(wordData, f, indent=4)
                print(f"✅ Saved: {mood} | {imageFilePath}")
            except Exception as e:
                print(f"❌ Error saving: {e}")
        else:
            print("❌ Failed to predict mood")
    
    print("✅ Processing complete!")

if __name__ == "__main__":
    word = input("Enter word (default: defy): ").strip() or "defy"
    processWordData(word)
