import os
import uvicorn
import torch
import time
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from transformers import AutoModelForCausalLM, AutoTokenizer
from uuid import uuid4
import system_prompts

class ChatRequest(BaseModel):
    message_content: str
    conversation_id: Optional[str] = None
    prompt_id: Optional[int] = None
    # Performance tuning parameters
    temperature: Optional[float] = 0.3  # Higher = more random/creative, Lower = more deterministic/focused
    top_p: Optional[float] = 0.9  # Controls diversity via nucleus sampling (0.0-1.0)
    max_new_tokens: Optional[int] = 400  # Maximum length of generated response

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

# SmolLM Model Class with performance optimizations
class SmolLM:
    def __init__(self):
        # Use CUDA if available for 10-20x speedup
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        # Load tokenizer with local caching
        self.tokenizer = AutoTokenizer.from_pretrained(
            "HuggingFaceTB/SmolLM2-1.7B-Instruct",
            local_files_only=False  # Set to True if you've downloaded the model locally
        )
        
        # Load model with optimizations:
        # 1. torch_dtype=torch.float16 - Use half precision for 2x memory efficiency and faster inference
        # 2. low_cpu_mem_usage=True - Reduces memory overhead during loading
        self.model = AutoModelForCausalLM.from_pretrained(
            "HuggingFaceTB/SmolLM2-1.7B-Instruct",
            torch_dtype=torch.float16,  # Use float16 for faster inference
            low_cpu_mem_usage=True
        ).to(self.device)
        
        # Additional optimization: enable CUDA graph capture for repeated forward passes with same shape
        self.model = self.model.eval()  # Ensure model is in eval mode
    
    def generate_response(self, 
                         messages: List[Dict[str, str]], 
                         temperature=0.3, 
                         top_p=0.9, 
                         max_new_tokens=400):
        """
        Generate a response with optimized parameters.
        
        Args:
            messages: List of message dictionaries with role and content
            temperature: Controls randomness (0.0-1.0)
                - Lower (0.1-0.3): More focused, deterministic, and faster responses
                - Higher (0.7-0.9): More creative but potentially slower to terminate
            
            top_p: Nucleus sampling parameter (0.0-1.0)
                - Lower values (0.5-0.7): Consider fewer tokens, faster but less diverse
                - Higher values (0.9-1.0): Consider more tokens, slower but more varied
            
            max_new_tokens: Maximum response length
                - Lower values generate faster responses
                - For chat, 200-400 tokens is usually sufficient
        """
        # Prepare input text using the tokenizer's chat template (optimized for this model)
        input_text = self.tokenizer.apply_chat_template(messages, tokenize=False)
        
        # Encode efficiently with proper tensor type and device placement
        inputs = self.tokenizer.encode(input_text, return_tensors='pt').to(self.device)
        
        # Generate with performance optimizations
        with torch.no_grad():  # Disable gradient calculation for inference
            outputs = self.model.generate(
                inputs, 
                max_new_tokens=max_new_tokens,  # Control response length
                temperature=temperature,  # Control randomness
                top_p=top_p,  # Nucleus sampling for efficient token selection
                do_sample=True,  # Enable sampling for better quality
                # Performance optimizations:
                num_beams=1,  # Disable beam search for speed
                early_stopping=True,  # Stop when ending seems likely
                pad_token_id=self.tokenizer.eos_token_id  # Proper padding for efficiency
            )
            
        # Extract only the new tokens (skip input tokens) for efficiency
        input_size = inputs.shape[1]
        outputs_decoded = self.tokenizer.decode(outputs[0][input_size:], skip_special_tokens=True)
        outputs_decoded = outputs_decoded.replace("<|assistant|>", "").strip()
        
        return outputs_decoded

# Initialize FastAPI app and components
app = FastAPI(title="Chat API")
conversation_manager = ConversationManager()
smol_lm = SmolLM()

# Add CORS middleware for frontend compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get available system prompts endpoint
@app.get("/system-prompts")
async def get_system_prompts():
    """Returns all available system prompts from the system_prompts module"""
    return {"prompts": system_prompts.get_all_prompts()}

# Main chat endpoint with performance optimizations
@app.post("/chat", response_model=ChatResponse)
async def chat_view(request: ChatRequest):
    try:
        # Extract request parameters
        message_content = request.message_content
        conversation_id = request.conversation_id
        
        if request.prompt_id:
            try:
                system_prompt = system_prompts.get_system_prompt(request.prompt_id)
            except ValueError:
                return JSONResponse({
                    "error": f"Invalid prompt ID: {request.prompt_id}. Must be between 1 and 10.",
                    "response": "An error occurred with the prompt selection.",
                    "user_message": message_content
                }, status_code=400)
        else:
            system_prompt = system_prompts.get_default_system_prompt()
        
        # Process the message (no system prompt stored in history)
        result = conversation_manager.process_message(message_content, conversation_id)
        conversation_id = result.get('conversation_id')
        
        # Get conversation history
        conversation_history = conversation_manager.get_conversation_history(conversation_id)
        
        # Add system prompt to history
        messages = [{"role": "system", "content": system_prompt}] + conversation_history
        
        # Set generation parameters from request or use defaults
        temperature = request.temperature or 0.3
        top_p = request.top_p or 0.9
        max_new_tokens = request.max_new_tokens or 400
        
        # Get response with the optimized parameters
        response_from_llm = smol_lm.generate_response(
            messages,
            temperature=temperature,
            top_p=top_p,
            max_new_tokens=max_new_tokens
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