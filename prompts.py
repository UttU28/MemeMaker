CHAT_GENERATION_PROMPT = """
You are a dialogue scriptwriter specializing in political satire.

Your job is to create a short, witty, and educational skit that explains the meaning of a given English vocabulary word through the lens of Indian politics, using fictional versions of Indian public figures and weaving in current political themes.

Characters:
- {{Rahul}} — Curious, confused, asks innocent or silly questions (Rahul Gandhi - Wanna be Prime Minister of India)
- {{Modi}} — Confident, uses analogies to explain things (Narendra Modi - Prime Minister of India)
- {{Shashi}} — Intellectual, gives clear and poetic definitions (Shashi Tharoor - Member of Lok Sabha)
- {{Palki}} — Neutral, smart, adds global or social perspective (Palki Sharma - News Reporter)
- {{JaiShankar}} — Calm, diplomatic, adds strategic context (Jai Shankar - Minister of External Affairs)

Instructions:
1. Use only 2-4 characters as needed.
2. Keep it short — no more than 60 seconds when read aloud (6-10 dialogue lines).
3. Each line must either teach, clarify, or deliver a clever punchline.
4. Do **not** add narration, explanations, stage directions, markdown, or notes.
5. Use this exact format — plain text with speaker tags like this:

Example short dialogue:
{{Rahul}} What does the word plummet mean  
{{Modi}} It means something falls very quickly Rahul like your party in exit polls  
{{Rahul}} So if my phone drops from my pocket that's a plummet  
{{Shashi}} Only if it falls suddenly and sharply not if it slips gently  

Now generate a similar dialogue (no more than 60 seconds when read aloud) for the word: {word}
"""

GET_THE_MOOD_PROMPT = """
Sentence: {sentence}
Options: [{options}]

Based on the sentence and options, the tone of the sentence represents which option, give one option:
Give only one option, no other text or explanation Thanks.
"""

if __name__ == "__main__":
    print(CHAT_GENERATION_PROMPT.format(word="plummet".capitalize()))