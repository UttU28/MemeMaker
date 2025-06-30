import os
import logging
from typing import List, Optional
from openai import OpenAI
from fastapi import HTTPException
from models import DialogueLine

logger = logging.getLogger(__name__)

def getOpenaiClient():
    apiKey = os.getenv('OPENAI_API_KEY')
    if not apiKey:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    return OpenAI(api_key=apiKey)

def loadScriptGenerationPrompt() -> str:
    try:
        import sys
        sys.path.append('src')
        from prompts import SCRIPT_GENERATION_PROMPT
        return SCRIPT_GENERATION_PROMPT
    except ImportError:
        return """
You are an expert dialogue scriptwriter specializing in political satire and educational content.

Your task is to create engaging, witty, and insightful dialogue scripts that bring complex topics to life through character interactions.

Selected Characters: {characters}
Topic/Situation: {topic}

Additional Context: {additional_context}

Generate a natural, engaging dialogue between these characters about the given topic. Format output as: {{Character}} their dialogue line
"""

async def generateScriptWithOpenai(selectedCharacters: List[str], prompt: str, word: Optional[str] = None) -> List[DialogueLine]:
    """Generate script using OpenAI API"""
    try:
        client = getOpenaiClient()
        
        scriptPromptTemplate = loadScriptGenerationPrompt()
        
        if word:
            topic = f"Explaining the concept/word: {word}"
            additionalContext = f"User's situation/context: {prompt}"
        else:
            topic = prompt
            additionalContext = "Focus on creating an engaging dialogue that explores this topic naturally."
        
        systemPrompt = f"""You are a dialogue scriptwriter. Create engaging conversations between characters about given topics.

Characters available: {', '.join(selectedCharacters)}
Always use the exact character names provided.
Format each line as: Character: dialogue text

Keep responses natural and engaging."""
        
        userPrompt = f"""
Create a dialogue script for the following:

Characters: {', '.join(selectedCharacters)}
Topic: {topic}
Context: {additionalContext}

Format each line as: Character: their dialogue
Example:
Modi: This is what I would say about this topic.
Palki: And this is my response to that point.

Keep it engaging and natural (4-6 lines total).
"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": systemPrompt},
                {"role": "user", "content": userPrompt}
            ],
            max_tokens=500,
            temperature=0.8
        )
        
        scriptText = response.choices[0].message.content.strip()
        logger.info(f"OpenAI generated script: {scriptText}")
        dialogueLines = []
        
        # Parse the script text into dialogue lines
        lines = scriptText.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Try different parsing formats
            character = None
            dialogueText = None
            
            # Format 1: Character: dialogue
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    character = parts[0].strip()
                    dialogueText = parts[1].strip()
            
            # Format 2: Character - dialogue
            elif ' - ' in line:
                parts = line.split(' - ', 1)
                if len(parts) == 2:
                    character = parts[0].strip()
                    dialogueText = parts[1].strip()
            
            # Format 3: **Character**: dialogue
            elif line.startswith('**') and '**:' in line:
                endIdx = line.find('**:', 2)
                if endIdx > 2:
                    character = line[2:endIdx].strip()
                    dialogueText = line[endIdx + 3:].strip()
            
            # Clean up character name (remove quotes, asterisks, etc.)
            if character:
                character = character.replace('"', '').replace("'", '').replace('*', '').strip()
                
                # Check if character name matches one of our selected characters (case insensitive)
                matched_character = None
                for selected_char in selectedCharacters:
                    if character.lower() == selected_char.lower():
                        matched_character = selected_char
                        break
                
                # If exact match not found, try partial match
                if not matched_character:
                    for selected_char in selectedCharacters:
                        if character.lower() in selected_char.lower() or selected_char.lower() in character.lower():
                            matched_character = selected_char
                            break
                
                if matched_character and dialogueText:
                    dialogueLines.append(DialogueLine(speaker=matched_character, text=dialogueText))
        
        if not dialogueLines:
            # Log the raw response for debugging
            logger.error(f"Failed to parse script. Raw response: {scriptText}")
            raise HTTPException(status_code=500, detail="Failed to parse generated script")
        
        return dialogueLines
        
    except Exception as e:
        logger.error(f"Error generating script with OpenAI: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate script: {str(e)}") 