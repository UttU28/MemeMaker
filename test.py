#!/usr/bin/env python3

import json
from src.llm import LlmService
from prompts import GET_THE_MOOD_PROMPT

def testOllamaLlama(sentence: str, speaker: str):
    llmService = LlmService()
    
    if not llmService.isOllamaRunning():
        print("Ollama not running")
        return
        
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

if __name__ == "__main__":
    speaker = "modi"
    sentence = "Defy, Rahul, is when someone goes against the rules or expectations, just like opposition parties defying my policies."
    mood, image_url = testOllamaLlama(sentence, speaker)
    print(f"Mood: {mood}")
    print(f"Image URL: {image_url}")
