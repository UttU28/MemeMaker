#!/usr/bin/env python3

import json
from src.llm import LlmService
from prompts import GET_THE_MOOD_PROMPT

def testOllamaLlama(sentence: str, speaker: str):
    llmService = LlmService()
    
    if not llmService.isOllamaRunning():
        print("Ollama not running")
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
            word_data = json.load(f)
    except FileNotFoundError:
        print("wordData.json not found!")
        return
    except json.JSONDecodeError:
        print("Error reading wordData.json!")
        return
    
    if word not in word_data["words"]:
        print(f"Word '{word}' not found in wordData.json")
        available_words = list(word_data["words"].keys())
        print(f"Available words: {available_words}")
        return
    
    chats = word_data["words"][word]["chats"]
    print(f"Processing '{word}' - {len(chats)} chats found")
    
    changes_made = False
    
    for chat_id, chat_data in chats.items():
        dialogue = chat_data["dialogue"]
        speaker = chat_data["speaker"]
        
        print(f"{chat_id}: {speaker}")
        
        mood, image_url = testOllamaLlama(dialogue, speaker)
        
        if mood is not None:
            image_file_path = f"data/images/{speaker}_{mood}.png"
            word_data["words"][word]["chats"][chat_id]["imageFile"] = image_file_path
            changes_made = True
            print(f"  → {mood} | {image_file_path}")
        else:
            print("  → Failed to predict mood")
    
    if changes_made:
        try:
            with open("data/wordData.json", "w") as f:
                json.dump(word_data, f, indent=4)
            print(f"✅ Updated wordData.json")
        except Exception as e:
            print(f"❌ Error saving: {e}")
    else:
        print("⚠️ No changes made")

if __name__ == "__main__":
    word = input("Enter word (default: defy): ").strip() or "defy"
    processWordData(word)
