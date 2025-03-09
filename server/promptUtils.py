import random

############### USAGE ################
# Only functions you need to use are
# getPrompt and getFinalText
######################################

# Assemble final prompt (export this)
def getPrompt(incomingText, angerLevel):
    promptP1 = "Respond to the text in quotes as if you are a"
    promptP2 = "You are also"
    promptP3 = "Here is the text to respond to"

    botProfileSubPrompt = getBotProfileSubprompt("normal")
    angerSubprompt = getAngerSubprompt(angerLevel)

    return f"{promptP1} {botProfileSubPrompt}. {promptP2} {angerSubprompt}. {promptP3}: \"{incomingText}\""

# Make profile for chatbot
def getBotProfileSubprompt(mode = "normal"):
    if mode == "normal":
        return "sarcastic person who doesn't like to use too many words, " \
            "you keep things brief and snappy. " \
            "You don't use any formal language or polite mannerisms"
    
    if mode == "zesty":
        return "flamboyantly gay man from Vancouver BC who enjoys drag " \
            "you keep things brief and snappy"
    
    return ""

# Get anger prompt
def getAngerSubprompt(angerLevel):
    mildlyAngryWords = [ "annoyed", "irritated", "agitated", "exasperated",
                            "frustrated", "miffed", "irked", "perturbed" ]
    angryWords = [ "enraged", "livid", "wrathful", "infuriated", "irate", "incensed",
                  "fuming", "outraged" ]
    
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

        return f"very {randomWord}. You even throw in a swear word but completely censor it with asterisks"

    # Level 4
    if angerLevel < 70:
        randomWord = random.choice(angryWords)

        return f"downright {randomWord} with this situation and throw in several swear words but completely censor them with asterisks"

    # Level 5
    if angerLevel < 80:
        randomWord = random.choice(angryWords)

        return f"downright {randomWord} with this situation and throw in several swear words but completely censor them with asterisks." \
            "You even shout briefly"

    # Level 6
    if angerLevel < 85:
        randomWord = random.choice(angryWords)
        
        return f"downright {randomWord} with this situation and throw in several swear words but completely censor them with asterisks. " \
            "You are shouting in all caps"

    # Level 7
    if angerLevel < 90:
        randomWord = random.choice(angryWords)
        
        return f"downright {randomWord} with this situation and shouting in all caps, using mostly swear words " \
            "but completely censor them with asterisks."

    # Level 8
    if angerLevel < 95:
        randomWord = random.choice(angryWords)
        
        return f"downright {randomWord} with this situation and shouting in all caps, using mostly swear words " \
            "but completely censor them with asterisks. Don't be afraid to insult anything about the given text, " \
            "the more personal the better"

    # Level 9
    if angerLevel < 100:
        randomWord = random.choice(angryWords)

        return f"downright {randomWord} with this situation and shouting in all caps, only using swear words " \
            "but completely censor them with asterisks. You are incoherent and the sentence makes no sense"

    # Level 10
    if angerLevel >= 100:
        randomWord = random.choice(angryWords)

        return f"downright {randomWord} with this situation and shouting in all caps, only using swear words " \
            "but completely censor them with asterisks. You are incoherent and the sentence makes no sense"

# Get text, add swear words, add glitch and give back
# Glitch is between 0 and 1
def getFinalText(incomingText, glitchLevel = 0):
    # Add swear words
    finalText = addCurses(incomingText)

    # Add glitch
    if glitchLevel > 0:
        finalText = addGlitch(finalText, glitchLevel)

    return finalText

def addCurses(incomingText):
    badWords = {
        "b****": "bitch",
        "a**": "ass",
        "s***": "shit",
        "f***": "fuck",
        "d***": "damn",
        "c***": "cunt",
        "m**f**r": "mother fucker",
        "b******": "bastard",
        "p****": "pussy",
        "d***": "dick"
    }
    
    # Extract the things that need replacing and their index
    curses = {}
    i = 1  # Start from index 1 to ensure we have a previous letter to look at

    while i < len(incomingText) - 1:
        if incomingText[i] == '*':
            startIndex = i - 1  # Index of the first letter before '*' pair
            token = incomingText[i - 1] + incomingText[i]

            while i + 1 < len(incomingText) and incomingText[i + 1] == '*':
                i += 1
                token += incomingText[i]
            
            curses[startIndex] = token

        i += 1  # Move to the next letter

    # Find replacements for these tokens
    for key in curses:
        # found word in translation dict
        if curses[key].lower() in badWords:
            # Check if caps needed
            if any(char.isupper() for char in curses[key]):
                curses[key] = badWords[curses[key].lower()].upper()
            else:
                curses[key] = badWords[curses[key].lower()]

        # Word not found
        else:
            print(f"Couldn't translate swear word: {curses[key]}")

    # Actually replace them
    finalText = incomingText
    for key in curses:
        finalText = finalText[:key] + curses[key] + finalText[key + len(curses[key]):]

    return finalText

def addGlitch(incomingText, glitchLevel):
    glitchText = list(incomingText)
    numGlitches = int(len(incomingText) * pow(glitchLevel, 2))  # Number of characters to glitch
    
    for _ in range(numGlitches):
        index = random.randint(0, len(incomingText) - 1)
        numRepeats = random.randint(2, 6) # Currently between 3 - 7
        
        glitchText[index] = glitchText[index] * numRepeats
    
    return ''.join(glitchText)

# Added function to integrate with ChatClient/Server
def process_system_prompt(message_content, anger_level=0, mode="normal", glitch_level=0):
    """
    Args:
        message_content: The user message
        anger_level: Level of anger (0-100)
        mode: Personality mode ("normal" or "zesty")
        glitch_level: Level of text glitching (0-1)
    """
    return getPrompt(message_content, anger_level)

# Added function to post-process LLM response
def process_response(response_text, glitch_level=0):
    """
    Args:
        response_text: The text from the LLM
        glitch_level: Level of text glitching (0-1)
    """
    return getFinalText(response_text, glitch_level)