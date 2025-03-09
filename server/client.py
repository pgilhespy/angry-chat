import requests
import json
from typing import Dict, Optional
import promptUtils

class ChatClient:
    """Client for interacting with the SmolLM chat API"""

    def __init__(self, base_url: str = None):
        """Base URL for the API (default: http://localhost:8000) local only"""
        self.base_url = base_url or "http://localhost:8000"
        self.chat_url = f"{self.base_url}/chat"
    
    def get_system_prompts(self) -> Dict:
        """Get all available system prompts"""
        try:
            response = requests.get(f"{self.base_url}/system-prompts")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error {response.status_code}: {response.text}")
                return {}
        except Exception as e:
            print(f"Error getting system prompts: {e}")
            return {}
    
    def chat(self, 
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
             max_new_tokens: int = None) -> Dict:
        """
        Example for javascript frontend, calling the chat endpoint

        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                conversation_id: conversationId,
                system_prompt: systemPrompt,
                anger_level: angerLevel,
                personality_mode: personalityMode,
                glitch_level: glitchLevel,
                use_prompt_utils: usePromptUtils,
                temperature: temperature,
                top_p: topP,
                max_new_tokens: maxNewTokens,
            }),
        });
        
        
        console.log(response.response)
        """
        """        
        Args:
            message: The user message
            conversation_id: Optional conversation ID for continuing a conversation
            system_prompt: Optional system prompt to define the AI's behavior
            
            # Personality parameters
            anger_level: Level of anger from 0-100
            personality_mode: Personality type ("normal" or "zesty")
            glitch_level: Level of text glitching from 0-1
            use_prompt_utils: Whether to use promptUtils for generating system prompt
            
            # Performance parameters
            temperature: Controls randomness (0.0-1.0)
                - Lower (0.1-0.3): More focused, deterministic responses
                - Higher (0.7-0.9): More creative, diverse responses
            
            top_p: Nucleus sampling parameter (0.0-1.0)
                - Lower values (0.5-0.7): Consider fewer tokens, less diverse
                - Higher values (0.9-1.0): Consider more tokens, more diverse
            
            max_new_tokens: Maximum response length
                - Lower values for faster responses
                - 100-200: Quick, shorter responses
                - 400-800: More detailed responses but slower
        """
        # Apply promptUtils if requested
        if use_prompt_utils and not system_prompt:
            system_prompt = promptUtils.process_system_prompt(
                message, 
                anger_level=anger_level,
                mode=personality_mode
            )
        
        # Build payload with required fields
        payload = {
            "message_content": message,
        }
        
        if conversation_id:
            payload["conversation_id"] = conversation_id
            
        if system_prompt:
            payload["system_prompt"] = system_prompt
            
        # Add personality parameters
        payload["anger_level"] = anger_level
        payload["personality_mode"] = personality_mode
        payload["glitch_level"] = glitch_level
        payload["use_prompt_utils"] = use_prompt_utils
            
        # Add performance parameters if provided
        if temperature is not None:
            # higher temperature makes the response more focused eg. less creative
            payload["temperature"] = min(max(temperature, 0.0), 1.0) # range is 0.0 to 1.0
            
        if top_p is not None:
            # higher top_p makes the response more diverse eg. more creative
            payload["top_p"] = min(max(top_p, 0.0), 1.0) # range is 0.0 to 1.0
            
        if max_new_tokens is not None:
            # more of this makes the response slower but more detailed
            payload["max_new_tokens"] = max(min(max_new_tokens, 1000), 1) # range is 1 to 1000
        
        try:
            # Make the API call
            response = requests.post(self.chat_url, json=payload)
            
            # Process response
            if response.status_code == 200:
                response_data = response.json()
                
                # Post-process the response if using promptUtils
                if use_prompt_utils and "response" in response_data:
                    response_data["response"] = promptUtils.process_response(
                        response_data["response"], 
                        glitch_level=glitch_level
                    )
                
                return response_data
            else:
                error_msg = f"Request failed with status code {response.status_code}"
                print(f"Error: {error_msg}")
                print(response.text)
                return {"error": error_msg}
                
        except Exception as e:
            error_msg = f"Exception during API call: {str(e)}"
            print(error_msg)
            return {"error": error_msg}