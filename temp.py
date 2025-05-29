import openai
import os
from dotenv import load_dotenv
from prompts import CHAT_GENERATION_PROMPT

load_dotenv()

client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def generateDialogue(word):
    formattedPrompt = CHAT_GENERATION_PROMPT.format(word=word.capitalize())
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": formattedPrompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        dialogue = response.choices[0].message.content.strip()
        return dialogue
        
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return None

if __name__ == "__main__":
    word = "defy"
    formattedWord = word.capitalize()
    
    print(f"Generating dialogue for word: {formattedWord}")
    print("-" * 50)
    
    dialogue = generateDialogue(formattedWord)
    
    if dialogue:
        print(dialogue)
    else:
        print("Failed to generate dialogue")