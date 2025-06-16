#!/usr/bin/env python3

import openai
import requests
import json
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class LlmService:
    
    def __init__(self):
        self.openaiClient = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.ollamaUrl = "http://localhost:11434"
        
    def generateWithOpenai(self, prompt: str, model: str = "gpt-3.5-turbo", 
                          maxTokens: int = 500, temperature: float = 0.7) -> Optional[str]:
        try:
            response = self.openaiClient.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=maxTokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ OpenAI error: {e}")
            return None
    
    def generateWithOllama(self, prompt: str, model: str = "llama3.2") -> Optional[str]:
        try:
            response = requests.post(
                f"{self.ollamaUrl}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                print(f"❌ Ollama error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Ollama error: {e}")
            return None
    
    def isOllamaRunning(self) -> bool:
        try:
            response = requests.get(f"{self.ollamaUrl}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def generate(self, prompt: str, provider: str = "openai", **kwargs) -> Optional[str]:
        if provider.lower() == "ollama":
            model = kwargs.get("model", "llama3.2")
            return self.generateWithOllama(prompt, model)
        else:
            model = kwargs.get("model", "gpt-3.5-turbo")
            maxTokens = kwargs.get("maxTokens", 500)
            temperature = kwargs.get("temperature", 0.7)
            return self.generateWithOpenai(prompt, model, maxTokens, temperature)
    
    def cleanResponse(self, response: str) -> str:
        if response:
            return response.replace('"', '').replace("'", '')
        return response 