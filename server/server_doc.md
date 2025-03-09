# ChatClient Documentation

## Overview

`ChatClient` is a Python client for interacting with the chat API. The client provides direct API calls to the custom `/chat` endpoint, supporting conversation management, custom system prompts, personality customization, and performance optimization.

## Features

- Send chat messages and receive AI-generated responses
- Maintain conversation context across multiple messages
- Use custom system prompts to control the AI's behavior
- Adjust personality parameters to change response style
- Apply text effects like glitches to responses
- Fine-tune response generation with performance parameters
- Retrieve available system prompts from the server

## Class: ChatClient

### Constructor

```python
ChatClient(base_url: str = None)
```
**Parameters:**
- `base_url` (optional): Base URL for the API. Defaults to "http://localhost:8000".

### Methods

#### get_system_prompts

```python
get_system_prompts() -> Dict
```

Retrieves all available system prompts from the server.

**Returns:**
A dictionary containing available system prompts.

#### chat

```python
chat(
    message: str, 
    conversation_id: str = None, 
    system_prompt: str = None,
    # Personality parameters
    anger_level: int = 0,
    personality_mode: str = "normal",
    glitch_level: float = 0,
    use_prompt_utils: bool = False,
    # Performance parameters
    temperature: float = None,
    top_p: float = None,
    max_new_tokens: int = None,
    censored: bool = False
) -> Dict
```

**Required Parameters:**
- `message`: The user message.

**Conversation Parameters:**
- `conversation_id` (optional): ID of an existing conversation to continue.
- `system_prompt` (optional): Custom system prompt to set the assistant's behavior.

**Personality Parameters:**
- `anger_level` (optional): Level of anger from 0-100.
  - `0`: Neutral, not angry
  - `20-40`: Mildly annoyed
  - `40-60`: Irritated, with mild swearing (censored)
  - `60-80`: Very angry with more swearing
  - `80-100`: Extremely angry, shouting, mostly swear words
  - Default: `0`

- `personality_mode` (optional): Personality type.
  - `"normal"`: Sarcastic person who keeps things brief
  - `"zesty"`: Flamboyantly gay man from Vancouver BC
  - Default: `"normal"`

- `glitch_level` (optional): Level of text glitching from 0-1.
  - `0`: No glitches
  - `0.1-0.3`: Minimal character repetition
  - `0.5-0.7`: Moderate glitching
  - `0.8-1.0`: Heavy text distortion
  - Default: `0`

- `use_prompt_utils` (optional): Whether to use promptUtils for generating system prompt.
  - When `true`, overrides any provided `system_prompt`
  - Default: `false`

- `censored` (optional): Controls profanity censoring.
  - `true`: Profanity is censored (e.g., "f***")
  - `false`: Profanity is displayed normally
  - Default: `false`

**Performance Parameters:**
- `temperature` (optional): Controls randomness (0.0-1.0)
  - Lower values (0.1-0.3): More focused, deterministic responses
  - Higher values (0.7-0.9): More creative, diverse responses
  - Default: `0.3`

- `top_p` (optional): Nucleus sampling parameter (0.0-1.0)
  - Lower values (0.5-0.7): Consider fewer tokens, less diverse
  - Higher values (0.9-1.0): Consider more tokens, more diverse
  - Default: `0.9`

- `max_new_tokens` (optional): Maximum response length
  - Lower values (50-150): Quick, shorter responses
  - Medium values (200-400): Balanced responses
  - Higher values (500+): Detailed but slower responses
  - Default: `400`

**Returns:**
A dictionary containing:
- `response`: The assistant's response.
- `user_message`: The original user message.
- `conversation_id`: ID for continuing the conversation.
- `error` (if an error occurred): Error message.

## Personality Customization

The client allows customizing the AI's personality through several parameters:

### Anger Level

Controls how angry the response will sound:
- **Level 0-20**: Slightly annoyed tone
- **Level 20-40**: Noticeably irritated
- **Level 40-60**: Very annoyed with mild swearing (censored)
- **Level 60-80**: Downright angry with more swearing
- **Level 80-100**: Extremely angry, incoherent shouting with excessive swearing

### Personality Mode

Defines the overall personality style:
- **"normal"**: A sarcastic person who keeps things brief and snappy, avoids formal language
- **"zesty"**: A flamboyantly gay man from Vancouver BC who enjoys drag culture

### Glitch Level

Applies text distortions to simulate glitches:
- **0**: No glitches
- **0.1-0.3**: Minimal character repetition 
- **0.5-0.7**: Moderate glitching, noticeable character duplication
- **0.8-1.0**: Heavy text distortion, potentially hard to read

## Performance Optimization

The client allows fine-tuning response generation through three key parameters:

### Temperature

Controls the randomness of the output:
- **Lower temperature (0.1-0.3)**: Produces more focused, consistent, and predictable responses. Good for factual or technical questions.
- **Higher temperature (0.7-0.9)**: Produces more creative, diverse, and unpredictable responses. Good for creative writing or brainstorming.
- **For speed**: Higher temperatures (0.7-0.8) can sometimes produce faster responses due to increased randomness.

### Top_p (Nucleus Sampling)

Controls the diversity of token selection:
- **Lower top_p (0.5-0.7)**: Considers fewer token options, resulting in more focused and potentially faster responses.
- **Higher top_p (0.9-1.0)**: Considers more token options, resulting in more diverse but potentially slower responses.
- **For speed**: Lower values (around 0.7-0.8) generally result in faster token selection.

### Max New Tokens

Controls the maximum length of the generated response:
- **Lower values (50-150)**: Short, concise responses generated quickly.
- **Medium values (200-400)**: Balanced between detail and generation time.
- **Higher values (500+)**: More comprehensive responses but takes longer to generate.
- **For speed**: Limit to 100-200 tokens for fastest responses.

## Usage Examples

### Basic Chat

```python
from client import ChatClient

client = ChatClient()
response = client.chat(message="Hello, how are you?")
print(response['response'])
```

### Using Personality Parameters

```python
# Create a moderately angry response
angry_response = client.chat(
    message="Why is my order late?",
    anger_level=60,
    personality_mode="normal",
    use_prompt_utils=True
)

# Create a zesty personality response with glitches
glitchy_response = client.chat(
    message="What do you think of this outfit?",
    personality_mode="zesty",
    glitch_level=0.3,
    use_prompt_utils=True
)
```

### Optimizing for Speed

```python
# Fast response configuration
quick_response = client.chat(
    message="Summarize quantum computing briefly",
    system_prompt="You are a helpful AI assistant that...",
    temperature=0.7,  # Higher randomness
    max_new_tokens=100,  # Short response
    top_p=0.7  # Fewer token options
)
```

### Optimizing for Detail

```python
# Detailed response configuration
detailed_response = client.chat(
    message="Explain the principles of quantum mechanics",
    system_prompt="You are a helpful AI assistant that provides thorough scientific explanations.",
    temperature=0.2,  # More focused
    max_new_tokens=500,  # Longer response
    top_p=0.95  # More token options
)
```

### Continuing a Conversation

```python
first_response = client.chat(message="What is Python?")
conv_id = first_response['conversation_id']

# Continue with different performance parameters
follow_up = client.chat(
    message="How is it different from JavaScript?",
    conversation_id=conv_id,
    temperature=0.3,
    max_new_tokens=300
)
```

## Response Format

The `chat()` method returns a dictionary with the following structure:

```python
{
    "response": "The AI-generated response to the message",
    "user_message": "Original message",
    "conversation_id": "unique-conversation-id-for-continuity"
}
```

In case of an error, the dictionary will include an additional `"error"` key with the error message.