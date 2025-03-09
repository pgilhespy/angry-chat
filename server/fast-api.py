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
    message_content: Optional[str] = None
    conversation_id: Optional[str] = None
    system_prompt: Optional[str] = None
    # Personality tuning parameters
    anger_level: Optional[int] = 0
    personality_mode: Optional[str] = "normal"
    glitch_level: Optional[float] = 0
    use_prompt_utils: Optional[bool] = True  # Always True by default
    # Performance tuning parameters
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    max_new_tokens: Optional[int] = 150
    # User data for personalization
    userData: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    user_message: str
    conversation_id: str

class ConversationManager:
    def __init__(self):
        # Using dictionary for O(1) lookup time
        self.conversations = {}
        # Track when conversations were last used for potential cleanup
        self.last_activity = {}
        
    def process_message(self, message_content: str, conversation_id: str = None) -> Dict[str, Any]:
        if not conversation_id:
            conversation_id = str(uuid4())
            
        # Create a new conversation list if it doesn't exist (faster than checking first)
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
            
        # Add user message directly to history (no system prompt in history)
        self.conversations[conversation_id].append({"role": "user", "content": message_content})
        
        # Update last activity timestamp
        self.last_activity[conversation_id] = time.time()
        
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
            # Update last activity timestamp
            self.last_activity[conversation_id] = time.time()
    
    def get_all_conversations(self) -> Dict[str, List[Dict[str, str]]]:
        """Return all stored conversations"""
        return self.conversations
    
    def clean_old_conversations(self, max_age_hours=24):
        """Clean up conversations older than max_age_hours"""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        # Find conversations to remove
        to_remove = []
        for conv_id, last_time in self.last_activity.items():
            if current_time - last_time > max_age_seconds:
                to_remove.append(conv_id)
                
        # Remove old conversations
        for conv_id in to_remove:
            if conv_id in self.conversations:
                del self.conversations[conv_id]
            if conv_id in self.last_activity:
                del self.last_activity[conv_id]
                
        return len(to_remove)  # Return number of removed conversations

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
        user_data = request.userData
                    
        # Handle case where only userData is provided (no message)
        if user_data and not message_content:
            return JSONResponse({
                "response": "User data received successfully",
                "user_message": "",
                "conversation_id": conversation_id or str(uuid4())
            })
        
        # Generate system prompt using promptUtils (always)
        system_prompt = promptUtils.process_system_prompt(
            message_content,
            anger_level=request.anger_level,
            mode=request.personality_mode,
            glitch_level=request.glitch_level,
            userData=request.userData
        )
        
        # Process the message
        result = conversation_manager.process_message(message_content, conversation_id)
        conversation_id = result.get('conversation_id')
        
        # Get conversation history
        conversation_history = conversation_manager.get_conversation_history(conversation_id)
        
        # Add system prompt to history
        messages = [{"role": "system", "content": system_prompt}] + conversation_history
        
        # Set generation parameters from request or use defaults
        temperature = request.temperature or 0.7
        top_p = request.top_p or 0.9
        max_new_tokens = request.max_new_tokens or 150
        
        # Get response from Claude API
        response_from_llm = claude_api.generate_response(
            messages,
            temperature=temperature,
            top_p=top_p,
            max_new_tokens=max_new_tokens
        )
        
        # Always apply text effects with promptUtils
        response_from_llm = promptUtils.process_response(
            response_from_llm,
            anger_level=request.anger_level,
            mode=request.personality_mode,
            glitch_level=request.glitch_level
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

# New endpoint to get all conversations
@app.get("/conversations")
async def get_conversations():
    """Get all stored conversations"""
    conversations = conversation_manager.get_all_conversations()
    return JSONResponse({
        "conversations": conversations,
        "count": len(conversations)
    })

# Cleanup endpoint for maintenance
@app.post("/cleanup")
async def cleanup_conversations(max_age_hours: int = 24):
    """Clean up conversations older than specified hours"""
    removed = conversation_manager.clean_old_conversations(max_age_hours)
    return JSONResponse({
        "removed": removed,
        "remaining": len(conversation_manager.conversations)
    })

def run_server(host='127.0.0.1', port=8000):
    print(f"Starting Chat API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == '__main__':
    run_server()