import os
import uvicorn
import time
import requests
import json
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from uuid import uuid4
import promptUtils
#import dotenv
from dotenv import load_dotenv

load_dotenv()

# Claude API class to replace the local model
class ClaudeAPI:
    def __init__(self, api_key=None):
        """Initialize Claude API client"""

        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Claude API key is required. Set ANTHROPIC_API_KEY environment variable or pass as parameter.")
        
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-haiku-20240307"  # Can be changed to any Claude model
    
    def generate_response(self, 
                         messages: List[Dict[str, str]], 
                         temperature=0.3, 
                         top_p=None, 
                         max_new_tokens=None):
        """
        Generate a response using Claude API
        
        Args:
            messages: List of message dictionaries with role and content
            temperature: Controls randomness (0.0-1.0)
            top_p: Not used by Claude API, included for compatibility
            max_new_tokens: Approximated to max_tokens for Claude
        """
        # Extract system prompt
        system_prompt = ""
        formatted_messages = []
        
        for message in messages:
            if message["role"] == "system":
                system_prompt = message["content"]
            else:
                formatted_messages.append({
                    "role": message["role"],
                    "content": message["content"]
                })
        
        # Create the request payload
        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "system": system_prompt,
            "temperature": temperature,
        }
        
        # Add max_tokens if specified (convert from max_new_tokens)
        if max_new_tokens:
            payload["max_tokens"] = max_new_tokens
            
        # Make the API request
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                response_data = response.json()
                return response_data["content"][0]["text"]
            else:
                error_msg = f"Claude API error: {response.status_code} - {response.text}"
                print(error_msg)
                return f"Error: {error_msg}"
                
        except Exception as e:
            error_msg = f"Exception during Claude API call: {str(e)}"
            print(error_msg)
            return f"Error: {error_msg}"

class ChatRequest(BaseModel):
    message_content: str
    conversation_id: Optional[str] = None
    system_prompt: Optional[str] = None
    # Personality tuning parameters
    anger_level: Optional[int] = 0  # Level of anger (0-100)
    personality_mode: Optional[str] = "normal"  # Personality mode ("normal" or "zesty")
    glitch_level: Optional[float] = 0  # Text glitch level (0-1)
    use_prompt_utils: Optional[bool] = False  # Whether to use promptUtils
    # Performance tuning parameters
    temperature: Optional[float] = 0.3  # Higher = more random/creative, Lower = more deterministic/focused
    top_p: Optional[float] = 0.9  # Not used by Claude but kept for compatibility
    max_new_tokens: Optional[int] = 400  # Approximated to max_tokens for Claude

class ChatResponse(BaseModel):
    response: str
    user_message: str
    conversation_id: str

class ConversationManager:
    def __init__(self):
        # Using dictionary for O(1) lookup time
        self.conversations = {}
        
    def process_message(self, message_content: str, conversation_id: str = None) -> Dict[str, Any]:
        if not conversation_id:
            conversation_id = str(uuid4())
            
        # Create a new conversation list if it doesn't exist (faster than checking first)
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
            
        # Add user message directly to history (no system prompt in history)
        self.conversations[conversation_id].append({"role": "user", "content": message_content})
        
        return {
            "conversation_id": conversation_id
        }
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, str]]:
        # Fast dictionary lookup with default empty list if not found
        return self.conversations.get(conversation_id, [])
        
    def add_assistant_message(self, conversation_id: str, content: str):
        # Only append if the conversation exists (avoid checks for better performance)
        if conversation_id in self.conversations:
            self.conversations[conversation_id].append({"role": "assistant", "content": content})

# Initialize FastAPI app and components
app = FastAPI(title="Chat API")
conversation_manager = ConversationManager()

# Initialize Claude API client
claude_api = ClaudeAPI()  # Will use ANTHROPIC_API_KEY from environment variables

# Add CORS middleware for frontend compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Main chat endpoint with performance optimizations
@app.post("/chat", response_model=ChatResponse)
async def chat_view(request: ChatRequest):
    try:
        # Extract request parameters
        message_content = request.message_content
        conversation_id = request.conversation_id
        
        # Use prompt utils if requested
        if request.use_prompt_utils:
            system_prompt = promptUtils.process_system_prompt(
                message_content,
                anger_level=request.anger_level,
                mode=request.personality_mode
            )
        # Use provided system prompt
        elif request.system_prompt:
            system_prompt = request.system_prompt
        # Fall back to default
        else:
            system_prompt = "You are a helpful assistant."
        
        # Process the message (no system prompt stored in history)
        result = conversation_manager.process_message(message_content, conversation_id)
        conversation_id = result.get('conversation_id')
        
        # Get conversation history
        conversation_history = conversation_manager.get_conversation_history(conversation_id)
        
        # Add system prompt to history
        messages = [{"role": "system", "content": system_prompt}] + conversation_history
        
        # Set generation parameters from request or use defaults
        temperature = request.temperature or 0.3
        top_p = request.top_p or 0.9  # Not used by Claude but kept for compatibility
        max_new_tokens = request.max_new_tokens or 400
        
        # Get response from Claude API
        response_from_llm = claude_api.generate_response(
            messages,
            temperature=temperature,
            top_p=top_p,  # This will be ignored by the Claude API
            max_new_tokens=max_new_tokens
        )
        
        # Apply text effects if using promptUtils
        if request.use_prompt_utils:
            response_from_llm = promptUtils.process_response(
                response_from_llm,
                glitch_level=request.glitch_level,
            )
        
        # Store the assistant's response in the conversation history
        conversation_manager.add_assistant_message(conversation_id, response_from_llm)
        
        # Return the response
        return JSONResponse({
            "response": response_from_llm,
            "user_message": message_content,
            "conversation_id": conversation_id
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse({
            "error": str(e),
            "response": "An error occurred while processing your request.",
            "user_message": request.message_content if hasattr(request, 'message_content') else "",
            "conversation_id": conversation_id if 'conversation_id' in locals() else None
        }, status_code=500)

def run_server(host='127.0.0.1', port=8000):
    print(f"Starting Chat API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == '__main__':
    run_server()