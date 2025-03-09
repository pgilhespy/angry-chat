import random

############### USAGE ################
# Only functions you need to use are
# process_system_prompt and process_response
######################################

# Assemble prompt for internal use
# Anger level is between 0-100 where 0 is chill and 100 is off the charts mad
def getPrompt(incomingText, angerLevel, mode="normal", glitchLevel=0, userData=None):
    promptP1 = "Respond to the text in quotes as if you are a"
    promptP2 = "You are also"
    promptP3 = "Here is the text to respond to"
    
    # Add user data context if available
    userData_context = ""
    if userData and isinstance(userData, dict):
        # Extract common user data fields
        name = userData.get('name', '')
        age = userData.get('age', '')
        gender = userData.get('gender', '')
        
        if any([name, age, gender]):
            userData_context = f"The user's name is {name}. " if name else ""
            userData_context += f"The user is {age} years old. " if age else ""
            userData_context += f"The user's gender is {gender}. " if gender else ""
            
            # Add instruction on how to use this data
            userData_context += "Use this information naturally in your responses, "
            
            # Add specific instructions based on anger level
            if angerLevel >= 60:
                userData_context += "especially when insulting them or expressing extreme frustration. "
                userData_context += "Make insults personal using their name or other details. "
            elif angerLevel >= 30:
                userData_context += "occasionally referring to them by name when annoyed. "
            else:
                userData_context += "occasionally referring to them by name in a friendly way. "
                
            userData_context += "Don't explicitly mention that you know this information. "

    botProfileSubPrompt = getBotProfileSubprompt(mode)
    angerSubprompt = getAngerSubprompt(angerLevel)
    
    # Construct the full prompt with user data context
    fullPrompt = f"{promptP1} {botProfileSubPrompt}. {promptP2} {angerSubprompt}. "
    if userData_context:
        fullPrompt += f"{userData_context} "
    fullPrompt += f"{promptP3}: \"{incomingText}\""
    
    #print(fullPrompt)  # For debugging
    return fullPrompt

# Set a profile for chatbot
def getBotProfileSubprompt(mode="normal"):
    # Common brevity instruction to add to all profiles
    brevity_instruction = "Keep your responses very brief - use 1-2 sentences maximum. " \
        "Be direct and to the point. No explanations, just answers. " \
        "Never use asterisks to narrate actions and don't describe your tone. " \
        "Use as few words as possible while still answering the question."
    
    if mode == "sarcastic":
        return "sarcastic person who doesn't like to use too many words. " \
            "You keep things extremely brief and snappy. " \
            "You don't use any formal language or polite mannerisms. " + brevity_instruction
    elif mode == "normal":
        return "direct and clear communicator. " \
            "You're helpful but extremely concise. " + brevity_instruction
    elif mode == "zesty":
        return "flamboyantly gay man from Vancouver BC who enjoys drag. " \
            "You keep things extremely brief. " + brevity_instruction
    else:
        # Default to normal mode if an unknown mode is provided
        return "direct and clear communicator. " \
            "You're helpful but extremely concise. " + brevity_instruction

# Get anger part of the prompt - MODIFIED FOR UNCENSORED SWEARING
def getAngerSubprompt(angerLevel):
    mildlyAngryWords = ["annoyed", "irritated", "agitated", "exasperated",
                        "frustrated", "miffed", "irked", "perturbed"]
    angryWords = ["enraged", "livid", "wrathful", "infuriated", "irate", "incensed",
                 "fuming", "outraged"]
    
    # Level 1
    if angerLevel < 20:
        randomWord = random.choice(mildlyAngryWords)

        return f"a little bit {randomWord}"

    # Level 2
    if angerLevel < 40:
        randomWord = random.choice(mildlyAngryWords)

        return f"quite {randomWord}"

    # Level 3
    if angerLevel < 60:
        randomWord = random.choice(mildlyAngryWords)

        return f"very {randomWord}. You occasionally use swear words like damn, ass, and shit"

    # Level 4
    if angerLevel < 70:
        randomWord = random.choice(angryWords)

        return f"downright {randomWord} with this situation and use several swear words like fuck, shit, and ass"

    # Level 5
    if angerLevel < 80:
        randomWord = random.choice(angryWords)

        return f"downright {randomWord} with this situation and frequently use swear words like fuck, shit, and asshole. " \
            "You even shout briefly"

    # Level 6
    if angerLevel < 85:
        randomWord = random.choice(angryWords)

        return f"downright {randomWord} with this situation and frequently use swear words. " \
            "You are shouting in all caps"

    # Level 7
    if angerLevel < 90:
        randomWord = random.choice(angryWords)

        return f"downright {randomWord} with this situation and shouting in all caps, using mostly swear words. " \
            "You're really fucking pissed off"

    # Level 8
    if angerLevel < 95:
        randomWord = random.choice(angryWords)

        return f"downright {randomWord} with this situation and shouting in all caps, using mostly swear words. " \
            "Don't be afraid to insult anything about the given text or the user, " \
            "the more personal the better. Use harsh language like asshole, motherfucker, etc."

    # Level 9
    if angerLevel < 100:
        randomWord = random.choice(angryWords)

        return f"downright {randomWord} with this situation and shouting in all caps, only using swear words. " \
            "You are so angry you're almost incoherent and the sentence barely makes sense. " \
            "Mix in words like fuck, shit, asshole, bitch, motherfucker, etc."

    # Level 10
    if angerLevel >= 100:
        randomWord = random.choice(angryWords)

        return f"completely {randomWord} beyond all reason, shouting in all caps, only using swear words. " \
            "You are totally incoherent with rage. String together profanities like " \
            "fuck, shit, cunt, motherfucker, asshole, bitch, etc."

# Get the text returned by the AI internally
# This is simplified since we don't need to uncensor anymore
def getFinalText(incomingText, angerLevel=0, mode="normal", glitchLevel=0):
    # No need to replace censored words since we're instructing the model
    # to use uncensored words directly in the prompt
    finalText = incomingText

    # Add glitch
    if glitchLevel > 0:
        finalText = addGlitch(finalText, glitchLevel)

    return finalText

# Add some glitch to the message
def addGlitch(incomingText, glitchLevel):
    glitchText = list(incomingText)
    numGlitches = int(len(incomingText) * pow(glitchLevel, 2))  # Number of characters to glitch
    
    for _ in range(numGlitches):
        index = random.randint(0, len(incomingText) - 1)
        numRepeats = random.randint(2, 6) # Currently between 3 - 7
        
        glitchText[index] = glitchText[index] * numRepeats
    
    return ''.join(glitchText)

# Added function to integrate with ChatClient/Server
def process_system_prompt(message_content, anger_level=0, mode="normal", glitch_level=0, userData=None):
    """
    Args:
        message_content: The user message
        anger_level: Level of anger (0-100)
        mode: Personality mode ("normal" or "zesty")
        glitch_level: Level of text glitching (0-1)
        userData: Dictionary with user information like name, age, gender
    """
    return getPrompt(message_content, anger_level, mode, glitch_level, userData)

# Added function to post-process LLM response
def process_response(response_text, anger_level=0, mode="normal", glitch_level=0):
    """
    Args:
        response_text: The text from the LLM
        anger_level: Level of anger (0-100)
        mode: Personality mode ("normal" or "zesty")
        glitch_level: Level of text glitching (0-1)
    """
    return getFinalText(response_text, anger_level, mode, glitch_level)