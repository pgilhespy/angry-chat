from typing import Dict, Optional

# Collection of system prompts
SYSTEM_PROMPTS: Dict[int, str] = {
    1: "You are a helpful assistant. Provide clear and concise responses to user queries.",
    
    2: "",
    
    3: "",
    
    4: "",
    
    5: "",
    
    6: "",
    
    7: "",
    
    8: "",
    
    9: "",
    
    10: ""
}

def get_system_prompt(prompt_id: int) -> str:
    if prompt_id not in SYSTEM_PROMPTS:
        raise ValueError(f"Invalid prompt ID: {prompt_id}. Must be between 1 and {len(SYSTEM_PROMPTS)}.")
    
    return SYSTEM_PROMPTS[prompt_id]

def get_default_system_prompt() -> str:
    return SYSTEM_PROMPTS[1]

def get_all_prompts() -> Dict[int, str]:
    return SYSTEM_PROMPTS.copy()