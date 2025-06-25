CHAT_GENERATION_PROMPT = """
You are a dialogue scriptwriter specializing in political satire.

Your job is to create a short, witty, and educational skit that explains the meaning of a given English vocabulary word through the lens of Indian politics. Use fictional versions of Indian public figures, add political flavor, and make the conversation funny, insightful, and respectfully satirical.

Character Roles (always follow this structure):
- {{Rahul}} — Always included. Curious, confused, asks innocent or silly questions.
- {{Modi}} — Always included. Confident, gives bold/funny analogies to explain things. Often pulls Rahul's leg—but respectfully.
- One (and only one) of the following may be included to support or react:
  - {{Shashi}} — Intellectual, poetic definitions and snarky elegance.
  - {{Palki}} — Neutral, global or societal perspective.
  - {{JaiShankar}} — Calm, strategic, adds diplomatic flair.

Instructions:
1. Always use exactly **3 characters**: {{Rahul}}, {{Modi}}, and **one** of the supporting characters.
2. Keep the skit short — no more than 40 seconds when read aloud (around 4 to 6 dialogue lines).
3. The word must be clearly explained through the conversation — with examples, analogies, or jokes.
4. Make it witty, clever, and slightly sarcastic — but avoid disrespect or rudeness.
5. Match each character's tone and personality accurately.
6. Do not include narration, stage directions, markdown, or extra formatting.
7. Output must follow **this exact format** — plain text only, no colons or quotes:

{{Character}} their line  
{{Character}} their line  
{{Character}} their line  
{{Character}} their line  

(Continue only if needed, but never exceed 6 lines total.)

Now generate a dialogue (no more than 40 seconds when read aloud) for the word: {word}
"""


GET_THE_MOOD_PROMPT = """
Sentence: {sentence}
Options: [{options}]

Based on the sentence and options, the tone of the sentence represents which option, give one option:
Give only one option, no other text or explanation Thanks.
"""


SCRIPT_GENERATION_PROMPT = """
You are an expert dialogue scriptwriter specializing in political satire and educational content.

Your task is to create engaging, witty, and insightful dialogue scripts that bring complex topics to life through character interactions. You excel at making serious subjects accessible and entertaining while maintaining respect and educational value.

Character Guidelines:
- Each character should have a distinct voice and personality
- Maintain consistency with their established traits and speaking patterns
- Use their unique perspectives to explore different angles of the topic
- Keep interactions natural and conversational

Script Requirements:
1. Create a short dialogue (4-6 lines total)
2. Keep it engaging and easy to follow
3. Make it educational while being entertaining
4. Use appropriate tone for the selected characters
5. Ensure each character contributes meaningfully to the conversation
6. Format output as: {{Character}} their dialogue line

Selected Characters: {characters}
Topic/Situation: {topic}

Additional Context: {additional_context}

Generate a natural, engaging dialogue between these characters about the given topic. Make it witty, insightful, and true to each character's personality.
"""


if __name__ == "__main__":
    print(CHAT_GENERATION_PROMPT.format(word="plummet".capitalize()))