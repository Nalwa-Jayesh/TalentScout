import os
import json
import requests
from pathlib import Path
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from typing import List, Dict, Optional

# Load environment variables
load_dotenv()

# Paths
CANDIDATE_DIR = Path("candidates")
CANDIDATE_DIR.mkdir(exist_ok=True)

# Get Hugging Face token from environment
HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACEHUB_API_TOKEN')
if not HUGGINGFACE_TOKEN:
    raise ValueError("HUGGINGFACEHUB_API_TOKEN not found in environment variables")

HF_MODEL = "google/gemma-2-2b" # Hugging Face model to use
OLLAMA_MODEL = "gemma2:2b" # Ollama model to use

class CandidateInfo:
    def __init__(self):
        self.full_name: str = ""
        self.email: str = ""
        self.phone: str = ""
        self.years_experience: int = 0
        self.desired_position: str = ""
        self.current_location: str = ""
        self.tech_stack: List[str] = []

def _query_ollama(prompt: str, max_tokens: int = 512) -> str:
    """Internal function to call local Ollama server using gemma2:2b"""
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": max_tokens, "num_gpu": 1},
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json().get("response", "")

def _query_huggingface(prompt: str, max_tokens: int = 512) -> str:
    """Internal function to call Hugging Face hosted inference for google/gemma-2-2b using pipeline."""
    try:
        # Initialize the pipeline
        text_generator = pipeline(
            "text-generation",
            model=HF_MODEL,
            token=HUGGINGFACE_TOKEN,
            device=0 # Use GPU if available (0 for first GPU), -1 for CPU
        )
        
        # Generate text using the pipeline
        # The pipeline returns a list of dictionaries, each with 'generated_text'
        generated_output = text_generator(
            prompt,
            max_new_tokens=max_tokens,
            temperature=0.7,
            top_p=0.95,
            repetition_penalty=1.2,
            do_sample=True,
            clean_up_tokenization_spaces=True
        )
        
        if generated_output and isinstance(generated_output, list) and 'generated_text' in generated_output[0]:
            return generated_output[0]['generated_text']
        else:
            raise ValueError("Unexpected response format from Hugging Face pipeline.")

    except Exception as e:
        # Catch errors during pipeline initialization or generation
        raise Exception(f"Failed to load or query Hugging Face via pipeline: {str(e)}")

def query_model(prompt: str, max_tokens: int = 512) -> str:
    """Query the model, with Ollama as primary and Hugging Face as fallback."""
    try:
        # Try Ollama first
        print("Attempting to query Ollama...")
        return _query_ollama(prompt, max_tokens)
    except requests.exceptions.RequestException as e:
        print(f"Ollama query failed: {e}. Falling back to Hugging Face.")
        try:
            # Fallback to Hugging Face
            print("Attempting to query Hugging Face...")
            return _query_huggingface(prompt, max_tokens)
        except Exception as hf_e:
            print(f"Hugging Face query also failed: {hf_e}")
            return "I apologize, but I'm currently unable to connect to the AI models. Please try again later."
    except Exception as e:
        print(f"An unexpected error occurred with Ollama: {e}. Falling back to Hugging Face.")
        try:
            # Fallback to Hugging Face for other Ollama errors
            print("Attempting to query Hugging Face...")
            return _query_huggingface(prompt, max_tokens)
        except Exception as hf_e:
            print(f"Hugging Face query also failed: {hf_e}")
            return "I apologize, but I'm currently unable to connect to the AI models. Please try again later."

def check_exit(message: str) -> bool:
    """Check for user intent to exit the conversation."""
    exit_commands = ["exit", "quit", "bye", "goodbye", "end"]
    return message.lower().strip() in exit_commands

def save_candidate_data(candidate_info: Dict) -> None:
    """Save candidate info to JSON."""
    try:
        name = candidate_info.get("full_name", "anonymous").replace(" ", "_")
        path = CANDIDATE_DIR / f"{name}.json"
        with open(path, "w") as f:
            json.dump(candidate_info, f, indent=2)
    except Exception as e:
        print(f"Error saving candidate data: {str(e)}")

def generate_technical_questions(tech_stack: List[str]) -> str:
    """Generate technical questions based on the candidate's tech stack."""
    prompt = f"""Based on the following tech stack, generate 3 relevant technical questions:
    Tech Stack: {', '.join(tech_stack)}
    
    Please provide questions that:
    1. Are specific to the technologies mentioned
    2. Test both theoretical knowledge and practical experience
    3. Are appropriate for a technical interview
    
    Format the response as a numbered list of questions."""
    
    # query_model now returns a single string
    return query_model(prompt)
