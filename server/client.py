import requests
import json
from typing import Dict, Optional
import promptUtils

class ChatClient:
    """Client for interacting with the Chat API"""

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
             message: str = None,
             conversation_id: str = None, 
             system_prompt: str = None,
             # Personality parameters
             anger_level: int = 0,
             personality_mode: str = "normal",
             glitch_level: float = 0,
             # Performance parameters
             temperature: float = None,
             top_p: float = None,
             max_new_tokens: int = None, 
             # User data
             userData: Dict = None) -> Dict:
        """
        Send a chat message to the API and get a response.
        
        Args:
            message: The user message (optional if only sending userData)
            conversation_id: Optional conversation ID for continuing a conversation
            system_prompt: Optional system prompt (will be used by promptUtils)
            
            # Personality parameters
            anger_level: Level of anger from 0-100
            personality_mode: Personality type ("normal", "sarcastic", or "zesty")
            glitch_level: Level of text glitching from 0-1)
                
            # Performance parameters
            temperature: Controls randomness (0.0-1.0)
            top_p: Nucleus sampling parameter (0.0-1.0)
            max_new_tokens: Maximum response length
                
            # User data
            userData: Dictionary with user information, such as:
                - name: User's name
                - age: User's age
                - gender: User's gender
        """
        # Build payload
        payload = {}
        
        # Only add message_content if it's provided
        if message:
            payload["message_content"] = message
        
        if conversation_id:
            payload["conversation_id"] = conversation_id
        
        if system_prompt:
            payload["system_prompt"] = system_prompt
        
        # Add personality parameters
        payload["anger_level"] = anger_level
        payload["personality_mode"] = personality_mode
        payload["glitch_level"] = glitch_level
        # No need to set use_prompt_utils since it's always True on the server
        
        # Add performance parameters if provided
        if temperature is not None:
            payload["temperature"] = min(max(temperature, 0.0), 1.0)
        
        if top_p is not None:
            payload["top_p"] = min(max(top_p, 0.0), 1.0)
        
        if max_new_tokens is not None:
            payload["max_new_tokens"] = max(min(max_new_tokens, 1000), 1)
        
        # Add user data if provided
        if userData is not None:
            payload["userData"] = userData
        
        try:
            # Make the API call
            response = requests.post(self.chat_url, json=payload)
            
            # Process response
            if response.status_code == 200:
                response_data = response.json()
                
                # Note: No need to post-process response here since the server does it
                print("response_data", response_data)
                print("payload", payload)
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
    
    # Get all conversations from the server
    def get_conversations(self) -> Dict:
        """Get all stored conversations from the server"""
        try:
            response = requests.get(f"{self.base_url}/conversations")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error {response.status_code}: {response.text}")
                return {"error": f"Request failed with status code {response.status_code}"}
        except Exception as e:
            error_msg = f"Exception during API call: {str(e)}"
            print(error_msg)
            return {"error": error_msg}
    
    # Clean up old conversations
    def cleanup_conversations(self, max_age_hours: int = 24) -> Dict:
        """Clean up conversations older than specified hours"""
        try:
            response = requests.post(f"{self.base_url}/cleanup", json={"max_age_hours": max_age_hours})
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error {response.status_code}: {response.text}")
                return {"error": f"Request failed with status code {response.status_code}"}
        except Exception as e:
            error_msg = f"Exception during API call: {str(e)}"
            print(error_msg)
            return {"error": error_msg}